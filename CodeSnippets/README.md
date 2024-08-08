
# DataLakeDirectorySizeCalculator

## Overview

The `DataLakeDirectorySizeCalculator` is a .NET application designed to interact with Azure Data Lake Storage Gen2. It calculates the total size of a specified directory by recursively listing all files within the directory and summing their sizes.

![image](https://github.com/user-attachments/assets/f0ac27d3-7188-4c53-a7b9-55f12e1e80ad)

## Purpose

This application aims to provide an efficient way to determine the size of a directory in Azure Data Lake Storage Gen2. By leveraging the `GetPathsAsync` method, it can recursively traverse directories and aggregate file sizes, offering insights into storage usage.

## Features

- **Recursive Directory Traversal**: The application lists all files within a specified directory and its subdirectories.
- **File Size Aggregation**: It calculates the total size by summing up the sizes of individual files.
- **Console Output**: The application outputs the name and size of each file as it processes them, providing real-time feedback.

## Usage

1. **Setup**: Configure the application with your Azure Storage account details, including the account name, account key, file system name, and directory path.
2. **Execution**: Run the application to calculate and display the total size of the specified directory.
3. **Output**: The application prints each file's name and size to the console, followed by the total directory size.

## Prerequisites

- **.NET SDK**: Ensure you have the .NET SDK installed.
- **Azure Storage Account**: You need an Azure Storage account with Data Lake Storage Gen2 enabled.
- **Access Credentials**: Obtain the storage account name and key for authentication.

## Key Components

- **DataLakeServiceClient**: Establishes a connection to the Azure Data Lake Storage account.
- **DataLakeFileSystemClient**: Provides access to the specified file system (container).
- **DataLakeDirectoryClient**: Handles interactions with the specified directory within the file system.
- **GetPathsAsync**: Recursively lists paths within the directory to gather file information.

## Getting Started

1. **Clone the Repository**: Download or clone the repository containing the source code.
2. **Configure Credentials**: Update the application with your Azure Storage account credentials.
3. **Run the Application**: Execute the application to calculate the directory size.

## Conclusion

The `DataLakeDirectorySizeCalculator` is a useful tool for managing and monitoring storage usage in Azure Data Lake Storage Gen2. It provides a straightforward approach to understanding the size of directories, which can be crucial for optimizing storage costs and performance.

For detailed implementation, refer to the source code in the repository.
