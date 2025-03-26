using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using System.Net.Http.Headers;
using Microsoft.AspNetCore.Mvc;
using webaiday.Models;

namespace webaiday.Controllers
{
    public class QueryController : Controller
    {
        private readonly IHttpClientFactory _httpClientFactory;
        private readonly string _apiUrl = "http://127.0.0.1:5000/query";

        public QueryController(IHttpClientFactory httpClientFactory)
        {
            _httpClientFactory = httpClientFactory;
        }

        // GET: /Query
        public IActionResult Index()
        {
            return View(new QueryViewResponse());
        }

        // POST: /Query
        [HttpPost]
        public async Task<IActionResult> Index(QueryViewResponse model)
        {
            Console.WriteLine("Query: " + model.Query);
            
                Console.WriteLine("Enviando solicitud al API...");
                var client = _httpClientFactory.CreateClient();
                client.DefaultRequestHeaders.Accept.Clear();
                client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

                Console.WriteLine("API URL: " + _apiUrl);
                // Crear el payload JSON con la consulta
                var jsonPayload = $"{{\"query\": \"{model.Query}\"}}";
                var content = new StringContent(jsonPayload, Encoding.UTF8, "application/json");

                // Enviar la solicitud POST al API Flask
                Console.WriteLine("Enviando solicitud POST al API...");
                var response = await client.PostAsync(_apiUrl, content);

                if (response.IsSuccessStatusCode)
                {
                    Console.WriteLine("Respuesta recibida del API.");
                    var responseData = await response.Content.ReadAsStringAsync();
                    Console.WriteLine("Respuesta: " + responseData);
                   // Deserializar el JSON de la respuesta
                    using JsonDocument doc = JsonDocument.Parse(responseData);
                    var root = doc.RootElement;
                    model.ApiResponse = root.GetProperty("response").GetString();
                    model.Context = root.GetProperty("context").GetString();
                    model.Prompt = root.GetProperty("prompt").GetString();

                    if (String.IsNullOrEmpty(model.ApiResponse))
                    {
                        model.ApiResponse = "No se recibió respuesta del API.";
                    }
                }
                else
                {
                    model.ApiResponse = $"Error en la llamada a la API. Código: {response.StatusCode}";
                    Console.WriteLine("Error en la llamada a la API. Código: " + response.StatusCode);
                }
            
            return View(model);
        }
    }
}
