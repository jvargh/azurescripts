/*
 * This code is provided "as-is" without any warranties or guarantees of any kind.
 * The author assumes no responsibility or liability for the use of this code.
 * Use at your own risk.
 */

using Azure;
using Azure.Storage;
using Azure.Storage.Files.DataLake;
using System;
using System.Threading.Tasks;

public class DataLakeHelper
{
    private readonly DataLakeServiceClient _serviceClient;
    private readonly DataLakeFileSystemClient _fileSystemClient;

    public DataLakeHelper(string accountName, string accountKey, string fileSystemName)
    {
        var serviceUri = new Uri($"https://{accountName}.dfs.core.windows.net");
        var storageSharedKeyCredential = new StorageSharedKeyCredential(accountName, accountKey);
        _serviceClient = new DataLakeServiceClient(serviceUri, storageSharedKeyCredential);
        _fileSystemClient = _serviceClient.GetFileSystemClient(fileSystemName);
    }

    public async Task<long> GetDirectorySizeAsync(string directoryPath)
    {
        try
        {
            var directoryClient = _fileSystemClient.GetDirectoryClient(directoryPath);
            long totalSize = 0;

            await foreach (var pathItem in directoryClient.GetPathsAsync(recursive: true))
            {
                if (pathItem.IsDirectory != true)
                {
                    Console.WriteLine($"File: {pathItem.Name}, Size: {pathItem.ContentLength.GetValueOrDefault()} bytes");
                    totalSize += pathItem.ContentLength.GetValueOrDefault();
                }
            }

            return totalSize;
        }
        catch (RequestFailedException ex) when (ex.ErrorCode == "PathNotFound")
        {
            Console.WriteLine($"Error: The specified path '{directoryPath}' does not exist.");
            throw;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Unexpected error: {ex.Message}");
            throw;
        }
    }
}

public class Program
{
    public static async Task Main(string[] args)
    {
        string accountName = "YourStorageAccountName";
        string accountKey = "YourStorageAccountKey";
        string fileSystemName = "YourFileSystemName";
        string directoryPath = "YourDirectoryPath";

        var dataLakeHelper = new DataLakeHelper(accountName, accountKey, fileSystemName);

        try
        {
            long totalSize = await dataLakeHelper.GetDirectorySizeAsync(directoryPath);
            Console.WriteLine($"Total size of directory '{directoryPath}': {totalSize} bytes");
        }
        catch (RequestFailedException ex) when (ex.ErrorCode == "PathNotFound")
        {
            Console.WriteLine("Please ensure the directory path is correct and exists.");
        }
        catch (Exception ex)
        {
            Console.WriteLine($"An error occurred: {ex.Message}");
        }
    }
}

