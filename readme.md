# RivaLLMatch

**RivaLLMatch** is an application that manages an arena in which different language models compete with each other. The basic concept is that models themselves evaluate each other.

![](./images/rivallmatch-header.png)

The competition takes place in one of the following areas:

* problem-solving
* creative writing
* debate and persuasion (tbd)

## How it works

Evaluation within the area is carried out as follows.

### Round setup 

The number of rounds (n_rounds) in which all models (n_llms) participate is predetermined

### Tasks selection

Models select the problems or tasks they will solve in each round. Models are queried sequentially until the task pool is filled. Each model is queried an equal number of times only if the number of rounds matches the number of models.

### Task solving in rounds

In each round, models are paired for competition. Each pair consists of a 'master' (who evaluates) and a 'student' (who provides the answer). For example, if n_llms=3, there are 6 possible pairs.

### Master-student clash
The 'student' model answers a task from the round, and the 'master' model evaluates the response based on the several criteria.

For problem-solving we consider following scores: 
* accuracy
* clarity
* depth of explanation
* reasoning

For creative writing we use such scores:
* creativity
* emotional depth
* narrative flow

### Next round

After completing a round, the next task is selected, and another round begins.

### Results compilation

RivaLLMatch collects the results and generates charts for each metric and the overall average for each model at the end of the session. Additionally, heat maps are created to visualize how models evaluated each other.

## Problem-solving results

### Task examples

LLMs are quite creative in generating problems that may be solved. Here are examples:

* **(gpt-4o)** Given a network of cities connected by bidirectional roads, each with a certain distance, you are tasked with developing
an algorithm to determine the shortest path between any two cities. The algorithm should take into consideration
multiple possible routes, varying distances, and should be efficient enough to handle a large number of cities and
roads. Additionally, you should describe how your algorithm ensures it finds the shortest path and any potential edge
cases it addresses.

* **(gpt-3.5-turbo-0125)** Can you explain how you would go about designing a sustainable transportation system for a rapidly growing city while
considering factors such as population density, infrastructure limitations, budget constraints, environmental impact,
and social equity?

* **(claude-3-opus-20240229)** Imagine you are tasked with designing a new transportation system for a rapidly growing city. The current system is
plagued by traffic congestion, inefficient routes, and aging infrastructure. The population is expected to double within
the next 20 years, and the city has limited financial resources to work with. Your goal is to create a sustainable,
efficient, and accessible transportation network that can accommodate the future growth of the city while also reducing
its environmental impact. Consider the various modes of transportation, such as buses, trains, bikes, and personal
vehicles, and how they can be integrated into a cohesive system. Also, take into account the diverse needs of the
population, including low-income residents, the elderly, and individuals with disabilities. Describe your proposed
transportation system in detail, explaining how it addresses the current challenges and meets the future needs of the
city.

* **(llama3-8b-8192)** Here is a complex problem that evaluates problem-solving skills:  Maria, a manager at a small software development
company, is faced with a staffing dilemma. The company has just landed a major new contract, but the increased workload
has stretched the existing team to its limits. Maria has been tasked with hiring new staff to meet the demand, but the
company's budget for this quarter has been drastically reduced due to unforeseen costs in a previous project. Maria has
been offered a talented young developer, Alex, who is interested in joining the company, but at a higher salary than the
company's usual range for new hires. On the other hand, Maria has also been approached by an experienced project
manager, Rachel, who is willing to join the company for a lower salary, but her skills are not directly applicable to
the new project.

### Overall scores
![](./results/problem_solving_average.png)

### Accuracy
![](./results/problem_solving_accuracy.png)
![](./results/problem_solving_accuracy_heatmap.png)

### Clarity
![](./results/problem_solving_clarity.png)
![](./results/problem_solving_clarity_heatmap.png)

### Depth of explanation
![](./results/problem_solving_depth.png)
![](./results/problem_solving_depth_heatmap.png)

### Reasoning
![](./results/problem_solving_reasoning.png)
![](./results/problem_solving_reasoning_heatmap.png)


## Creative writing results

### Examples of problems

Here is the list of tasks for the competition, generated by different models:

**(gpt-4o)** A world where emotions manifest as physical creatures that people must care for and interact with, leading to unexpected
bonds and challenges.

**(gpt-3.5-turbo-0125)** A day in the life of a detective in a small town.

**(claude-3-opus-20240229)** A mysterious, ancient artifact is discovered in a remote village, and strange events begin to occur, causing the
villagers to question its origins and power.

**(llama3-8b-8192)** A mysterious library hidden deep within an ancient forest, where the books whisper secrets to those who dare to listen.

**(mixtral-8x7b-32768)** Explore the emotions and challenges of a talented young musician who moves to a new city to pursue their dreams, but
struggles to find their place and make a name for themselves in the competitive and cutthroat world of music."

**(gemini-1.0-pro-latest)** A young woman discovers a hidden world beneath the surface of her mundane life.


### Overall scores
![](./results/creative_writing_average.png)

### Creativity
![](./results/creative_writing_creativity.png)
![](./results/creative_writing_creativity_heatmap.png)

### Emotional depth
![](./results/creative_writing_depth.png)
![](./results/creative_writing_depth_heatmap.png)

### Narrative flow
![](./results/creative_writing_flow.png)
![](./results/creative_writing_flow_heatmap.png)

