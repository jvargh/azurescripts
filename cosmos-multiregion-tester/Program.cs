using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.Azure.Cosmos;

namespace CosmosDBFailoverTest
{
    class Program
    {
        private static readonly string EndpointUri = "https://<your-cosmosdb-account>.documents.azure.com:443/";
        private static readonly string PrimaryKey = "<your-primary-key>";
        private static readonly string DatabaseName = "my-database";
        private static readonly string ContainerName = "my-container";
        private static readonly string PartitionKeyPath = "/pk1"; // Change the partition key here to reflect in the entire code

        private static CosmosClient cosmosClient;
        private static Database database;
        private static Container container, testContainer;

        static async Task Main(string[] args)
        {
            try
            {
                Console.WriteLine("Starting Cosmos DB operations...");

                //// Initialize Cosmos Client
                //cosmosClient = new CosmosClient(EndpointUri, PrimaryKey);

                //// Create DB and Seed data
                //await CreateDBAndSeed();

                //// Test Multi-Region Writes
                //await TestMultiRegionWritesAsync();

                //// Test Manual Failover
                //await TestFailoverAsync();

                //// Verify Data Consistency
                //await VerifyDataConsistencyAsync();

                //// Validate Cosmos Consistencies
                //await TestConsistencyLevelsAsync();

                Console.WriteLine("All tests completed successfully.");
            }
            catch (CosmosException ex)
            {
                Console.WriteLine($"Cosmos DB Error: {ex.StatusCode} - {ex.Message}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
            finally
            {
                if (cosmosClient != null)
                {
                    cosmosClient.Dispose();
                }
            }
        }

        private static async Task CreateDBAndSeed()
        {
            // Get or Create Database
            database = await cosmosClient.CreateDatabaseIfNotExistsAsync(DatabaseName);
            Console.WriteLine($"Database: {DatabaseName} created/retrieved successfully.");

            // Get or Create Container
            container = await database.CreateContainerIfNotExistsAsync(
                new ContainerProperties
                {
                    Id = ContainerName,
                    PartitionKeyPath = PartitionKeyPath
                }
            );
            Console.WriteLine($"Container: {ContainerName} created/retrieved successfully.");

            // Seed Data
            await SeedSampleDataAsync();
            Console.WriteLine("Sample data seeded successfully.");
        }

        private static async Task SeedSampleDataAsync()
        {
            var partitionKeyPropertyName = PartitionKeyPath.TrimStart('/'); // Extract the property name from the partition key path
            var startTime = DateTime.UtcNow;

            Console.WriteLine("Starting 1-minute data insertion...");

            while (DateTime.UtcNow - startTime < TimeSpan.FromMinutes(1))
            {
                var item = new Dictionary<string, object>
                {
                    { "id", Guid.NewGuid().ToString() },
                    { partitionKeyPropertyName, $"Category{new Random().Next(1, 100)}" }, // Generate random category
                    { "name", $"Item{new Random().Next(1, 1000)}" },
                    { "description", "Automatically generated item" },
                    { "createdDate", DateTime.UtcNow }
                };

                try
                {
                    var partitionKeyValue = item[partitionKeyPropertyName]?.ToString();

                    if (partitionKeyValue == null)
                    {
                        throw new InvalidOperationException($"Partition key value for '{partitionKeyPropertyName}' is missing in the item.");
                    }

                    var response = await container.CreateItemAsync(item, new PartitionKey(partitionKeyValue));
                    Console.WriteLine($"Inserted item with id: {item["id"]}, Request Charge: {response.RequestCharge}");
                }
                catch (CosmosException ex) when (ex.StatusCode == System.Net.HttpStatusCode.Conflict)
                {
                    Console.WriteLine($"Item with id: {item["id"]} already exists. Skipping...");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error inserting item with id {item["id"]}: {ex.Message}");
                }
            }

            Console.WriteLine("1-minute data insertion completed.");
        }

        private static async Task TestMultiRegionWritesAsync()
        {
            var preferredRegions = new List<string> { "East US 2", "Central US", "West US" }; // Update with your regions
            Console.WriteLine("Testing multi-region writes...");

            foreach (var region in preferredRegions)
            {
                Console.WriteLine($"\nTesting writes to preferred region: {region}");

                var cosmosClientOptions = new CosmosClientOptions
                {
                    ApplicationPreferredRegions = new List<string> { region }
                };

                CosmosClient client = new CosmosClient(EndpointUri, PrimaryKey, cosmosClientOptions);
                Container testContainer = client.GetContainer(DatabaseName, ContainerName);

                try
                {
                    for (int i = 0; i < 5; i++)
                    {
                        var item = new Dictionary<string, object>
                {
                    { "id", Guid.NewGuid().ToString() },
                    { PartitionKeyPath.TrimStart('/'), $"Category{i}" },
                    { "name", $"MultiRegionItem{i}" },
                    { "description", $"Write test for region: {region}" },
                    { "createdDate", DateTime.UtcNow }
                };

                        var response = await testContainer.CreateItemAsync(
                            item,
                            new PartitionKey(item[PartitionKeyPath.TrimStart('/')].ToString())
                        );

                        Console.WriteLine($"Inserted item in region '{region}': {item["id"]}, Request Charge: {response.RequestCharge}");
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error during multi-region write test in region '{region}': {ex.Message}");
                }
            }

            Console.WriteLine("\nMulti-region writes test completed.");
        }


        private static async Task TestFailoverAsync()
        {
            var applicationPreferredRegions = new List<string> { "East US 2", "Central US", "West US" }; // Update with your regions
            var cosmosClientOptions = new CosmosClientOptions();

            Console.WriteLine("Testing manual failover from each preferred region...");

            foreach (var region in applicationPreferredRegions)
            {
                Console.WriteLine($"\nSetting preferred region to: {region}");

                // Update preferred region dynamically
                cosmosClientOptions.ApplicationPreferredRegions = new List<string> { region };
                CosmosClient client = new CosmosClient(EndpointUri, PrimaryKey, cosmosClientOptions);
                testContainer = client.GetContainer(DatabaseName, ContainerName);

                try
                {
                    // Fetch an existing item from the container
                    var (itemId, partitionKeyValue) = await GetExistingItemAsync();

                    // Read the fetched item
                    var response = await testContainer.ReadItemAsync<dynamic>(itemId, new PartitionKey(partitionKeyValue));
                    Console.WriteLine($"Successfully read item from {region}: {response.Resource}");
                }
                catch (CosmosException ex)
                {
                    Console.WriteLine($"Error reading item from {region}: {ex.StatusCode} - {ex.Message}");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Unexpected error reading item from {region}: {ex.Message}");
                }
            }
        }

        private static async Task<(string, string)> GetExistingItemAsync()
        {
            if (testContainer == null)
            {
                throw new InvalidOperationException("Container is not initialized. Ensure the Cosmos DB client and container are properly set up.");
            }

            var query = new QueryDefinition("SELECT TOP 1 c.id, c.pk1 FROM c"); // Replace "pk1" with your partition key property name
            using FeedIterator<dynamic> resultSet = testContainer.GetItemQueryIterator<dynamic>(query);

            while (resultSet.HasMoreResults)
            {
                foreach (var item in await resultSet.ReadNextAsync())
                {
                    string id = item.id;
                    string partitionKeyValue = item.pk1; // Replace "pk1" with your partition key property name
                    return (id, partitionKeyValue);
                }
            }

            throw new InvalidOperationException("No items found in the container.");
        }

        private static async Task VerifyDataConsistencyAsync()
        {
            // List of valid Azure regions for Cosmos DB
            var validAzureRegions = new List<string>
            {
                "East US", "West US", "Central US", "North Europe", "West Europe", "East US 2",
                "East Asia", "Southeast Asia", "Japan East", "Japan West", "Australia East",
                "Australia Southeast", "Canada Central", "Canada East", "UK South", "UK West"
                // Add all valid regions supported by Cosmos DB
            };

            var applicationPreferredRegions = new List<string> { "East US 2", "Central US", "West US" }; // Replace with your test regions
            var cosmosClientOptions = new CosmosClientOptions();

            Console.WriteLine("Verifying data consistency across all regions...");

            // To track stats across regions
            Dictionary<string, (int itemCount, long latencyMs)> regionStats = new Dictionary<string, (int, long)>();

            foreach (var region in applicationPreferredRegions)
            {
                if (!validAzureRegions.Contains(region))
                {
                    Console.WriteLine($"Skipping invalid region: {region}");
                    regionStats[region] = (0, -1); // Mark as invalid
                    continue;
                }

                Console.WriteLine($"\nSetting preferred region to: {region}");

                // Update preferred region dynamically
                cosmosClientOptions.ApplicationPreferredRegions = new List<string> { region };
                CosmosClient client = new CosmosClient(EndpointUri, PrimaryKey, cosmosClientOptions);
                Container testContainer = client.GetContainer(DatabaseName, ContainerName);

                try
                {
                    // Query data to verify consistency
                    var query = new QueryDefinition("SELECT * FROM c");
                    using FeedIterator<dynamic> resultSet = testContainer.GetItemQueryIterator<dynamic>(query);

                    Console.WriteLine($"Querying data from region: {region}");
                    int itemCount = 0;
                    var stopwatch = System.Diagnostics.Stopwatch.StartNew(); // Measure latency

                    while (resultSet.HasMoreResults)
                    {
                        var items = await resultSet.ReadNextAsync();
                        itemCount += items.Count;
                    }

                    stopwatch.Stop();
                    long latencyMs = stopwatch.ElapsedMilliseconds;

                    // Store stats for the region
                    regionStats[region] = (itemCount, latencyMs);

                    Console.WriteLine($"Region: {region}, Item Count: {itemCount}, Latency: {latencyMs} ms");
                }
                catch (CosmosException ex)
                {
                    Console.WriteLine($"Error querying data from {region}: {ex.StatusCode} - {ex.Message}");
                    regionStats[region] = (0, -1); // Mark as failure
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Unexpected error querying data from {region}: {ex.Message}");
                    regionStats[region] = (0, -1); // Mark as failure
                }
            }

            // Display overall stats summary
            Console.WriteLine("\n--- Consistency Verification Summary ---");
            foreach (var regionStat in regionStats)
            {
                string region = regionStat.Key;
                var stats = regionStat.Value;
                string status = stats.latencyMs >= 0 ? "Success" : "Invalid/Failed";
                Console.WriteLine($"Region: {region}, Status: {status}, Item Count: {stats.itemCount}, Latency: {stats.latencyMs} ms");
            }

            Console.WriteLine("Data consistency verification completed.");
        }

        private static async Task TestConsistencyLevelsAsync()
        {
            var consistencyLevels = new List<ConsistencyLevel>
            {
                ConsistencyLevel.Strong,
                ConsistencyLevel.BoundedStaleness,
                ConsistencyLevel.Session,
                ConsistencyLevel.Eventual,
                ConsistencyLevel.ConsistentPrefix
            };

            // Add a variable for the current account-level consistency
            var accountLevelConsistency = ConsistencyLevel.Session; // Replace with the actual account consistency if known

            Console.WriteLine("Testing the effect of varying consistency levels on performance and cost...");

            foreach (var consistencyLevel in consistencyLevels)
            {
                // Skip if the requested level is stronger than the account-level consistency
                if (IsStrongerConsistencyLevel(consistencyLevel, accountLevelConsistency))
                {
                    Console.WriteLine($"Skipping {consistencyLevel} as it is stronger than the account's default consistency ({accountLevelConsistency}).");
                    continue;
                }

                Console.WriteLine($"\nSetting consistency level to: {consistencyLevel}");

                var cosmosClientOptions = new CosmosClientOptions
                {
                    ConsistencyLevel = consistencyLevel
                };

                CosmosClient client = new CosmosClient(EndpointUri, PrimaryKey, cosmosClientOptions);
                Container testContainer = client.GetContainer(DatabaseName, ContainerName);

                try
                {
                    var query = new QueryDefinition("SELECT * FROM c");
                    using FeedIterator<dynamic> resultSet = testContainer.GetItemQueryIterator<dynamic>(query);

                    Console.WriteLine($"Querying data with {consistencyLevel} consistency...");
                    int itemCount = 0;
                    double totalRequestCharge = 0;
                    var stopwatch = System.Diagnostics.Stopwatch.StartNew();

                    while (resultSet.HasMoreResults)
                    {
                        var response = await resultSet.ReadNextAsync();
                        itemCount += response.Count;
                        totalRequestCharge += response.RequestCharge;
                    }

                    stopwatch.Stop();
                    long latencyMs = stopwatch.ElapsedMilliseconds;

                    Console.WriteLine($"Consistency Level: {consistencyLevel}");
                    Console.WriteLine($"Item Count: {itemCount}");
                    Console.WriteLine($"Total Request Charge (RUs): {totalRequestCharge}");
                    Console.WriteLine($"Latency: {latencyMs} ms");
                }
                catch (CosmosException ex)
                {
                    Console.WriteLine($"Error querying data with {consistencyLevel} consistency: {ex.StatusCode} - {ex.Message}");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Unexpected error with {consistencyLevel} consistency: {ex.Message}");
                }
            }

            Console.WriteLine("\nConsistency level testing completed.");
        }

        // Helper method to determine if one consistency level is stronger than another
        private static bool IsStrongerConsistencyLevel(ConsistencyLevel requestedLevel, ConsistencyLevel accountLevel)
        {
            var consistencyHierarchy = new List<ConsistencyLevel>
            {
                ConsistencyLevel.Strong,
                ConsistencyLevel.BoundedStaleness,
                ConsistencyLevel.Session,
                ConsistencyLevel.ConsistentPrefix,
                ConsistencyLevel.Eventual
            };

            return consistencyHierarchy.IndexOf(requestedLevel) < consistencyHierarchy.IndexOf(accountLevel);
        }

    }
}
