from siteUtil import *

history = "Instruction: Here we are simulating conversation, you are an AI talking to Nolan, only complete the next AI's response in the conversation's history and do not use words like <<SYS>>, [INST], [AI]. Here is the conversation history: "

while True:
    str = input("User: ")
    history+="Nolan: "+str +"\nAI: "

    str2 = get_gpt3_response(history).strip()
    print("AI: "+ str2)
    history+=  str2




