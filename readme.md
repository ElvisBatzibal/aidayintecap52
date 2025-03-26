https://www.truper.com/CatVigente/productosNuevos?page=1


https://github.com/pgvector/pgvector



ollama list

ollama pull ollama-llama2-7b

// Ejemplo: API Controller para buscar y presentar ficha técnica generada
[HttpGet("producto/{id}/ficha-tecnica")]
public async Task<IActionResult> GetFichaTecnica(int id)
{
    // 1. Consultar datos del producto en la base de datos relacional
    var producto = await _productoRepository.GetProductoById(id);

    // 2. Consultar la base vectorial para obtener similitudes (esto podría hacerse vía una API REST)
    var embedding = await _vectorService.GetEmbeddingByProductId(id);

    // 3. Invocar el modelo generativo con el contenido de specs y embedding (opcional)
    var fichaGenerada = await _generativeAIService.GenerateFichaTecnica(producto.Specs);

    return Ok(new {
        producto.Nombre,
        producto.Categoria,
        FichaTecnica = fichaGenerada
    });
}