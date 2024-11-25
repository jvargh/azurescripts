        var foundproduct = (await _products.FindAsync(p => p.Name.Contains("Yamba"))).FirstOrDefault();
        Console.WriteLine("Queried and returned record: " + foundproduct.Name);
 
        foreach (var server in sesHwnd.Client.Cluster.Description.Servers)
        {
            if(server.State == MongoDB.Driver.Core.Servers.ServerState.Connected)
            {
                Console.WriteLine("Endpoint {0} is connected, ReasonChanged: {1}, Type: {2}", server.EndPoint, server.ReasonChanged.ToString(), server.Type.ToString());
            }
        }
