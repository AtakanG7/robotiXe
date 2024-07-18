import random
from langchain.chat_models.openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain import PromptTemplate
from langchain.text_splitter import CharacterTextSplitter

QUESTION_GENERATION_PROMPT = PromptTemplate.from_template("""
    Given context generate 5 questions out of given context never give your opinion. If the information is not enough to 
    generate 5 questions, you must say "please provide more information". You must add options like a, b, c and d as possible answers to each generated questions.
                        
    context = {context}
""")

class QuestionGenerator:
    def __init__(self, text, temperature, api_key):
        self.text = text
        self.temperature = temperature
        self.api_key = api_key

    def generate(self):
        chunks = self._create_text_chunks()
        sampled_chunks = self._sample_chunks(chunks)
        chain = self._create_question_generation_chain()
        
        # Join the sampled chunks into a single string
        context = "\n\n".join(sampled_chunks)
        
        # Pass the context as a dictionary to the chain
        return chain({"context": context})

    def _create_text_chunks(self, chunk_size=2000, chunk_overlap=300):
        splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
        return splitter.split_text(self.text)

    def _sample_chunks(self, chunks, n=5):
        return random.sample(chunks, min(n, len(chunks)))

    def _create_question_generation_chain(self):
        llm = ChatOpenAI(temperature=self.temperature/10, model_name="gpt-3.5-turbo", openai_api_key=self.api_key)
        return LLMChain(llm=llm, prompt=QUESTION_GENERATION_PROMPT)