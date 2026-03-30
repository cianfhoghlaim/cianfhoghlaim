using System.Diagnostics;
using Gaois.QueryLogger;
using Microsoft.AspNetCore.Mvc;
using Samples.AspNetCore.Models;

namespace Samples.AspNetCore.Controllers
{
    public class HomeController : Controller
    {
        private readonly IQueryLogger _queryLogger;

        public HomeController(IQueryLogger queryLogger)
        {
            _queryLogger = queryLogger;
        }

        public IActionResult Index()
        {
            var query = new Query
            {
                QueryTerms = "tested"
            };

            _queryLogger.Log(query);

            return View();
        }

        public IActionResult About()
        {
            ViewData["Message"] = "Your application description page.";

            return View();
        }

        public IActionResult Contact()
        {
            ViewData["Message"] = "Your contact page.";

            return View();
        }

        public IActionResult Privacy()
        {
            return View();
        }

        [ResponseCache(Duration = 0, Location = ResponseCacheLocation.None, NoStore = true)]
        public IActionResult Error()
        {
            return View(new ErrorViewModel { RequestId = Activity.Current?.Id ?? HttpContext.TraceIdentifier });
        }
    }
}
