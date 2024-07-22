Make LLM write like JC

## Prepare Prompts
For each Blog

1. We get the blog from MongoDB
2. Preprocess to clean it up(remove code and links)
3. We process them into body(organized sentences) and metadatas(TOC, title, type)
4. We feed in the whole blog context into Haiku and tries to get a question for each sentence by feeing it in Anthropic Haiku
5. We prepares finetuning like this
```
System: Write like JC
Role: A question for each sentence
User: (One sentence from JC's Blog)
```

