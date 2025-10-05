# 25-2_DSL_Modeling_NLP2_HospitalAgent

# Hospital Reservation System with Multi-Agent Orchestration

> This project was conducted by the **Natural Language Processing Team 2** as part of the 2025 Fall modeling project at [**Data Science Lab, Yonsei University**](https://github.com/DataScience-Lab-Yonsei).



## Team

| Cohort | Members                            |
|--------|------------------------------------|
| 12th   | Eunhee Kim, Kunwoo Kim |
| 13th   | Sehyun Park (Leader)        |
| 14th   | Dongjun Shin, Junho Yeo        |


---

## Coverpage

![Cover Image](./fig/cover.png)

For more detailed explanations, methodology, and analysis, please refer to the [project report](https://docs.google.com/viewer?url=https://raw.githubusercontent.com/jwlee9941/SCOPE/main/report/report.pdf)


---

## How to Run Code

```bash
# First, start the RAG server
cd rag_doctor_agent && python a2a_wrapper.py

# Run LangGraph
cd ../ && langgraph dev

# There are two ways to interact: through the LangGraph Studio UI or the custom interface.
# LangGraph Studio UI automatically launches in the browser when you run `langgraph dev`, but it requires signup and setup.
# Below launches the custom interface that allows you to use your terminal to interact with the agent.

python chat_interface.py
```

---

## Results

### Qualitative Results



### Quantitative Results



---

## License

-
