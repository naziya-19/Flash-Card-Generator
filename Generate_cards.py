import os
import json
# from langchain.chat_models import AzureChatOpenAI
from langchain_openai import AzureChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from typing import Literal, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.utils.function_calling import convert_to_openai_function, format_tool_to_openai_function
from langchain_core.output_parsers import PydanticOutputParser

os.environ['AZURE_OPENAI_API_KEY'] = 'api_key'
os.environ['AZURE_OPENAI_API_TYPE'] = 'azure'
os.environ['AZURE_OPENAI_API_VERSION'] = '2024-02-01'
os.environ['AZURE_OPENAI_ENDPOINT'] = 'https://ragapp1.openai.azure.com/'

class CardsModel(BaseModel):
  """Store each question and answer in the following format"""
  question: str = Field(description="Flash Card Question")
  answer: str = Field(description="Flash Card Answer.")
  difficulty:Literal['HARD', 'MEDIUM', 'EASY'] = Field(description="Dificulty Level of the Question.")

class CardsList(BaseModel):
  """Call this with individually extracted question answers"""
  card_list: List[CardsModel] = Field(description="Store each Flash Card")


llm = AzureChatOpenAI(
    api_version=os.environ['AZURE_OPENAI_API_VERSION'],
    azure_deployment='chat-endpoint'
  )

    
def split_text ( text):
  text_splitter = RecursiveCharacterTextSplitter(
      # Set a really small chunk size, just to show.
      chunk_size=512,
      chunk_overlap=50,
      length_function=len,
      is_separator_regex=False,
      separators=["\n\n","\n","  ",".", " ",""]
  )
  documents = text_splitter.create_documents([text])
  return documents

def create_chain(text, subject, grade):
  messages = [
    ('system', 'You are a studious student studying in grade {grade} expert in {subject}. To strategize study you generate effective flash cards and pop quizzes.'),
    ('human', """
        Thought: There is pargraph which may contain some important information.
        -= paragraph =-
        {text}
        Action: You understand the contextual meaning of the paragraph and take out some important Q and A facts.
        validation: You rate it as HIGH, MEDIUM and LOW. According to the importance and difficulty of your Questions.
        The endproduct should be as follow:
        question: Your Question
        Answer: Your Answer
        Difficulty: Difficulty Category
        """)
]

  parser  = PydanticOutputParser(pydantic_object=CardsList) 

  chat_template = ChatPromptTemplate.from_messages(messages)

  model_with_function = llm.bind(functions=[convert_to_openai_function(CardsList)])

  chain = chat_template | llm.with_structured_output(schema=CardsList)
  
  result = chain.invoke(input={'text':text, 'subject': subject, 'grade': grade})
  return result


def Generate_Flash_Cards( context, subject, grade):
  docs = split_text(context)
  qa_list=[]
  for doc in docs:
    text = doc.page_content
    result = create_chain(text, subject, grade)
    temp = json.loads(result.json())['card_list']
    qa_list+=temp
  
  return qa_list
