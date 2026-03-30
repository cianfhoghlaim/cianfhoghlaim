using Aspire.Hosting;

var builder = DistributedApplication.CreateBuilder(args);

// 添加后端项目
var api = builder.AddProject<Projects.KoalaWiki>("koalawiki");

// 添加前端项目
// var frontend = builder.AddNpmApp("frontend", "../../web-site", "dev")
//     .WithReference(api)
//     .WithHttpEndpoint(env: "PORT", targetPort: 3000, port: 31000);

builder.Build().Run();