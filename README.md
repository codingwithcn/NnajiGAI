# NnajiGAI
A grocery Chatbot for my family, runs in the background, while it listens for incoming commands 

How to get started with NnajiGAI
> 1. First pip install it or download it through github.com
> 2. Create a virtualenv or not, it does not matter, what does matter is you use python 3.8 because thats what I use.
> 3. Pip install all the required packages
> 4. Open up the database and then add all the users you would like the computer to look for commands from. 
>>> A. Name: The name of the user

>>> B. Number: The user number, if the user does not have a number, but has a email put in the email without the @gmail.com or @icloud.com etc

>>> C. Provider: This is where you would look for your provider mine was @metropcs.com but if you are not sure. I suggest texting your email and that should show you, your providers @

> 5. Once you have set the user table in the database. You are now ready to run the program. Do not worry about the other tables. The computer will take care of that.

Different Commands and What they do
> You could always look at the cj_commands.text file for the commands    
> But you could also: 
>> Text: "What can you do?": This will force the computer to send you a random command from its command list. Giving you information on what it can do. 

>> Text: "Add to groceries: (the name of the grocery item you would want to add)": This will add the item name into that weeks grocceries

>> Text: "Delete from grocceries: (the name of the item you would like to delete)": This will delete the item from that weeks grocceries. 

>> Text: "Show grocceries": This will show you that weeks grocceries

>> Text: "Program End Password: Legacy": This will forcebly quit the code. Meaning you would have to manually start it up again

More updates coming. Any questions and issues feel free to contact me at codingwithcn@gmail.com