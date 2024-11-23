from langchain.tools import BaseTool
from kdb_faiss import KDBFaiss



import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold




##################################################### GEMINI LLM



class Gemini(object):
    def __init__(self, model_name, apikey, system_prompt, generation_config=None):
        self.history = []
        self.chat_session = None
        # Aplicacao dos chunks e criacao do modelo
        self.model = self.__create_model(apikey, model_name, 
                                         system_prompt, generation_config)
        
    def __create_model(self, apikey, model_name, system_prompt, generation_config=None):
        genai.configure(api_key=apikey)
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        if generation_config is None:
            generation_config = {
                'temperature': 0.2,
                'max_output_tokens': 1000
            }
        return genai.GenerativeModel(
            model_name,
            system_instruction=system_prompt,
            generation_config = generation_config,
            safety_settings=safety_settings
        )

    def interact(self, prompt):
        return self.model.generate_content(prompt).text


    def chat(self, query):
        if self.chat_session is None:
            self.chat_session = self.model.start_chat(
                history=[]
            )
        # print(user_prompt)
        message = {
            'role': 'user',
            'parts': [query]
        }
        response = self.chat_session.send_message(message)
        self.history.append(message)
        self.history.append({
            'role': 'model',
            'parts': [response.text]
        })
        return response.text
        



##################################################### KDB FAISS



class KDBFaissTool(BaseTool):
    def __init__(self, dbpath, name, description):
        self.name = name # "String Reversal Tool"
        self.description = description # "use esta ferramenta quando precisar inverter uma string"
        self.dbpath = dbpath
        self.db = KDBFaiss.import_kdb(dbpath)


    def _run(self, query: str):
        response = self.db.search(self, query, k = 10, index_type = 'both')
        response = [f"- {x}" for x in response]
        response = '\n'.join(response)
        return response


    def _arun(self, query: str):
      raise NotImplementedError("Async não suportado pelo StringReverseTool")







