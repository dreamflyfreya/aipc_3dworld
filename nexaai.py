from nexa.gguf import NexaTextInference

model_path = "E:\\Desktop\\llama"
inference = NexaTextInference(
    model_path=model_path,
    local_path=None,
    stop_words=[],
    temperature=0.7,
    max_new_tokens=512,
    top_k=50,
    top_p=0.9,
    profiling=True
)

# run() method
inference.run()

# run_streamlit() method
inference.run_streamlit(model_path)

# create_embedding(input) method
inference.create_embedding("Hello, world!")

# create_chat_completion(messages)
inference.create_chat_completion(
    messages=[{"role": "user", "content": "write a long 1000 word story about a detective"}]
)

# create_completion(prompt)
inference.create_completion("Q: Name the planets in the solar system? A:")