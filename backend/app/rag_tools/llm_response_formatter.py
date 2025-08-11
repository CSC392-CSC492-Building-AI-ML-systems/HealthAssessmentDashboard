# TODO: Create a function called reformat(user_query: str, data_dict: Dict[str, Any], prediction: str)

# Create a prompt to give to the LLM (OpenAI) to output an appropriate response (potentially using the arguments data_dict and prediction as variables in the prompt)

# Note that the response outputted from the LLM at this step of the RAG pipeline is the FINAL response that the user will receive when returned from the ChatbotService to the API, followed by the client directly after. As such, it should respect some general conditions:

# The response should be aware of Canadian customs and law regarding pharma

# The response should remain formal and speak in the context of medicine/drugs

# The response should address the proposed question directly 