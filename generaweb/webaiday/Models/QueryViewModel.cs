namespace webaiday.Models;

public class QueryViewModel
{
    public string Query { get; set; }
}

public class QueryViewResponse
    {
        public string Query { get; set; }
        public string Context { get; set; }
        public string Prompt { get; set; }
        public string ApiResponse { get; set; }
    }
