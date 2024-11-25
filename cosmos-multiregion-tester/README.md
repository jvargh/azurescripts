# Azure Cosmos DB Multi-Region Testing

This project demonstrates various operations and configurations in Azure Cosmos DB, focusing on **multi-region writes**, **failover scenarios**, **data consistency**, and **consistency level testing**. It includes a pre-configured ARM template to set up the Cosmos DB account and the necessary infrastructure.

---

## **Table of Contents**
1. [Getting Started](#getting-started)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Code Overview](#code-overview)
5. [Running the Project](#running-the-project)
6. [Comparison of Multi-Region Writes vs. Single Write Region](https://github.com/jvargh/azurescripts/blob/main/cosmos-multiregion-tester/README.md#comparison-of-multi-region-writes-vs-single-write-region)
7. [Contributing](#contributing)
8. [License](#license)

---

## **Getting Started**
To get started with this project, deploy the ARM template to set up the Azure Cosmos DB infrastructure, configure the application with the required details, and then run the project.

---

## **Features**
- **Multi-Region Writes Testing**: Tests and validates write operations across multiple regions.
- **Failover Simulation**: Verifies how the application behaves during manual failovers in a Cosmos DB setup.
- **Data Consistency Validation**: Checks for data replication across regions using the configured consistency level.
- **Consistency Levels Evaluation**: Tests the performance and cost of different Cosmos DB consistency levels.

---

## **Prerequisites**

### **1. Deploy the ARM Template**
To deploy the required Azure Cosmos DB infrastructure:
1. Use the provided ARM template to create a Cosmos DB account with the necessary configuration.

#### Deployment Steps:
1. Deploy the ARM template using Azure CLI, PowerShell, or the Azure Portal:
   ```bash
   az deployment group create \
     --resource-group <your-resource-group> \
     --template-file cosmosdb-arm-template.json
   ```
2. The ARM template will:
   - Create a Cosmos DB account with **multi-region writes enabled**. In this example following regions were used: "East US 2", "Central US", "West US".
   - Configure the database and container.
   - Enable multiple regions for replication.

3. Note the following from the deployment output:
   - **Account Endpoint URI**
   - **Primary Key**

### **2. Configure the Application**
Update the application with the details from the ARM deployment:
- Following .NET Nuget packages were used:
![image](https://github.com/user-attachments/assets/e251a8ec-5be6-444e-857c-8876490e700f)
- In the `Program.cs` file or `appsettings.json`, replace placeholders with:
  - `EndpointUri`: Cosmos DB Account URI.
  - `PrimaryKey`: Cosmos DB Account Key.

---

## **Code Overview**
The project code executes the following steps sequentially:

1. **Initialize Cosmos Client**:
   - Connects to the Cosmos DB account using the provided endpoint and key.

2. **Create Database and Seed Data**:
   - Ensures the database and container are created.
   - Seeds initial data into the container for testing.

3. **Test Multi-Region Writes**:
   - Validates the ability to write to multiple regions and checks for successful data replication.
![image](https://github.com/user-attachments/assets/c4e1419c-f3c0-44cc-84c0-406e557d3e47)

4. **Simulate Manual Failover**:
   - Simulates failover scenarios to verify application behavior when a region fails.
![image](https://github.com/user-attachments/assets/156bab24-838d-4066-844b-d5e5f0f13527)

5. **Verify Data Consistency**:
   - Confirms data replication across regions based on the account’s consistency level.
![image](https://github.com/user-attachments/assets/1323610c-e6da-40ee-9147-197e76c580bc)

6. **Test Consistency Levels**:
   - Evaluates the performance impact and cost of different consistency levels, including Strong, Bounded Staleness, Session, Eventual, and Consistent Prefix.
![image](https://github.com/user-attachments/assets/ad93776f-a65e-4b87-832f-732fa611cb7d)

---

## **Running the Project**

1. **Deploy the ARM Template**:
   - Follow the instructions in the [Prerequisites](#prerequisites) section to deploy the Cosmos DB infrastructure.

2. **Run the Application**:
   - Build and run the project:
     ```bash
     dotnet run
     ```

3. **Observe the Output**:
   - The application will display the results of each operation, including:
     - Data replication across regions.
     - Performance and RU costs for each consistency level.
     - Results of failover scenarios.

---

### **Comparison of Multi-Region Writes vs. Single Write Region**
This table summarizes the key differences between Multi-Region Writes and Single Write Region configurations in Azure Cosmos DB across functionality, cost, and performance aspects.
| **Category**           | **Aspect**             | **Multi-Region Writes**                                                                 | **Single Write Region**                                                       |
|-------------------------|------------------------|-----------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| **Functionality**       | **Write Availability** | Enables writes in all configured regions, improving availability during regional outages | Writes are only allowed in the primary region; failover required for other regions |
|                         | **Conflict Resolution** | Requires conflict resolution mechanisms (e.g., Last-Write-Wins or custom policies)       | No conflict resolution required since all writes are directed to one region   |
|                         | **Consistency**       | Strong Consistency not supported; Bounded Staleness is the strongest available          | All consistency levels, including Strong Consistency, are supported          |
|                         | **Failover Behavior** | Failover does not disrupt writes; other regions can continue writing seamlessly         | Write operations stop until a failover promotes a secondary region to primary |
|                         | **Application Design** | Applications must handle potential data conflicts and rely on conflict resolution        | Simpler application design due to centralized write location                 |
| **Cost**               | **RU (Request Units)** | Write operations may incur slightly higher RU costs due to maintaining multiple replicas| Lower RU costs as writes are replicated only from one region to others       |
|                         | **Storage Costs**     | No difference; storage costs depend on data volume and replication                      | No difference; storage costs depend on data volume and replication           |
|                         | **Provisioned Throughput** | Requires write throughput to be provisioned independently for each region              | Write throughput is only provisioned for the primary region                 |
|                         | **Data Transfer Costs** | Increased cross-region data transfer costs for synchronizing writes between regions    | Lower cross-region transfer costs as writes are replicated only from primary |
| **Performance**         | **Write Latency**     | Lower latency for writes when the application is closer to the region being written to  | Higher latency for applications writing from regions far from the primary    |
|                         | **Read Latency**      | No difference; both support local read replicas in all regions for low-latency reads    | No difference; both support local read replicas in all regions for low-latency reads |
|                         | **Conflict Handling** | Applications may experience slight delays or complexity when resolving conflicts         | No conflict handling overhead                                                |
|                         | **Replication**       | Writes are replicated asynchronously across all write regions                           | Writes are replicated asynchronously to secondary read regions only          | 

---

## **Contributing**
Contributions are welcome! Please fork the repository, make changes, and submit a pull request.

---

## **License**
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

