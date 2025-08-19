## CSINTSY Prolog Chatbot
<p align="justify">
This project introduces a logic-based chatbot that processes and responds to family relationship queries using a Prolog inference engine. The chatbot operates through a command-line interface, accepting declarative statements and relational questions. To simplify the Python implementation, core familial relationships and gender roles are encoded in Prolog, while more complex inference logic and validation are handled in Python through multiple targeted Prolog queries. The chatbot does not infer gender and requires it to be explicitly declared in most cases. It accepts consistent facts, rejects contradictory inputs, and ensures logical consistency in its responses. Special cases such as incestuous relationships handling are excluded to reduce complexity and maintain focus on the defined scope of interaction.<br>
</p>
Created by:<br> Alyanna Lim <br>
Brianna Salvador<br>
Carl Vincent Ko <br>
Del Castillo, Jose Mari<br><br>
Submission Date: August 6, 2025

##

<p align="center"><b>Chatbot Strengths</b></p>
<p align="center" style="margin: 10px 0;">
  <img src="https://github.com/user-attachments/assets/fb71f4d5-c829-4641-802e-27077dd6fa4b" alt="Inferred Grandfather Relationship" />
  <br>
  <em>Figure 1. Inferred Grandfather Relationship</em>
</p>

<p align="center" style="margin: 10px 0;">
  <img src="https://github.com/user-attachments/assets/e3afaef1-4ef2-49e2-b140-fad50738ef1b" alt="Gender Check" />
  <br>
  <em>Figure 2. Gender Check</em>
</p>

<p align="center" style="margin: 10px 0;">
  <img src="https://github.com/user-attachments/assets/6afa5171-4cc3-48f2-8448-1480829298c4" alt="Ancestor Check" />
  <br>
  <em>Figure 3. Ancestor Check</em>
</p>

<p align="center" style="margin: 10px 0;">
  <img src="https://github.com/user-attachments/assets/781ab340-9134-4793-8e7f-c8dff903e7d8" alt="Identity Check" />
  <br>
  <em>Figure 4. Identity Check</em>
</p>

<p align="center" style="margin: 10px 0;">
  <img src="https://github.com/user-attachments/assets/0518ba16-b425-46ae-ac2a-03863773731b" alt="Descendant Check" />
  <br>
  <em>Figure 5. Descendant Check</em>
</p>

<p align="center" style="margin: 10px 0;">
  <img src="https://github.com/user-attachments/assets/e6d63376-7f4e-42a6-a663-ad84e2519713" alt="Shared-parent check" />
  <br>
  <em>Figure 6. Shared-parent check</em>
</p>

<p align="center" style="margin: 10px 0;">
  <img src="https://github.com/user-attachments/assets/6af5547d-7617-4989-b7fa-b6726e40d1d4" alt="Requires known parent-sibling relationship to confirm uncle/aunt" />
  <br>
  <em>Figure 7. Requires known parent-sibling relationship to confirm uncle/aunt</em>
</p>

<p align="center" style="margin: 10px 0;">
  <img src="https://github.com/user-attachments/assets/7ade4e0a-2a3e-4c07-943b-1d416a31f119" alt="Aunt relationship inference" />
  <br>
  <em>Figure 8. Aunt relationship inference</em>
</p>

<p align="center" style="margin: 10px 0;">
  <img src="https://github.com/user-attachments/assets/304699dd-8f5d-485e-922c-a096eac5df5b" alt="Uncle relationship inference" />
  <br>
  <em>Figure 9. Uncle relationship inference</em>
</p>

<p align="center" style="margin: 10px 0;">
  <img src="https://github.com/user-attachments/assets/95fd45cd-eab8-4551-9c01-78bdc7d1e8a4" alt="Proper handling for invalid prompts" />
  <br>
  <em>Figure 10. Proper handling for invalid prompts</em>
</p><br>
<p align="center"><b>Chatbot Weaknesses</b></p>
<p align="center" style="margin: 10px 0;">
  <img src="https://github.com/user-attachments/assets/214e18c1-7458-4982-b14d-205d756c2412" alt="Requires gender for children of or child of" />
  <br>
  <em>Figure 11. Requires gender for children of or child of</em>
</p>

<p align="center" style="margin: 10px 0;">
  <img src="https://github.com/user-attachments/assets/1bd7d444-9285-4c67-bfc8-d7cc94d00a0a" alt="Requires both genders for are the parents of" />
  <br>
  <em>Figure 12. Requires both genders for are the parents of</em>
</p>

<p align="center" style="margin: 10px 0;">
  <img src="https://github.com/user-attachments/assets/c4c14fb5-8e48-45ec-a888-0c3101882cd9" alt="No handling for incestuous relationships" />
  <br>
  <em>Figure 13. No handling for incestuous relationships</em>
</p>




