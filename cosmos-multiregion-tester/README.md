# Azure Cosmos DB Multi-Region Testing

This project demonstrates various operations and configurations in Azure Cosmos DB, focusing on **multi-region writes**, **failover scenarios**, **data consistency**, and **consistency level testing**. It includes a pre-configured ARM template to set up the Cosmos DB account and the necessary infrastructure.

---

## **Table of Contents**
1. [Getting Started](#getting-started)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Code Overview](#code-overview)
5. [Running the Project](#running-the-project)
6. [Contributing](#contributing)
7. [License](#license)

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
   - Create a Cosmos DB account with **multi-region writes enabled**.
   - Configure the database and container.
   - Enable multiple regions for replication.

3. Note the following from the deployment output:
   - **Account Endpoint URI**
   - **Primary Key**

### **2. Configure the Application**
Update the application with the details from the ARM deployment:
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

## **Contributing**
Contributions are welcome! Please fork the repository, make changes, and submit a pull request.

---

## **License**
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

