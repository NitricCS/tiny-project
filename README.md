# Parser and Type System for Tiny
This project contains a parser and a type system for a made-up language called **Tiny**.\
It parses the code using a grammar and checks for basic syntax and type errors as well as local scope overflows.

You can checkout the repo directly: https://github.com/NitricCS/tiny-project.git

The project uses a SLY-based symbol table project as a base: https://github.com/NitricCS/symbol-table-sly

## Description
* [Main logic](./docs/main_logic.md)
* [Lexer](./docs/lexer.md)
* [Type system methods](./docs/typing.md)
* [Logger](./docs/logger.md)

## Installation and Usage
There are two options to run the project on your local machine, both with up- and downsides.

The _./code_ folder contains sample programs that can be used as test inputs. Those programs are taken from the task PDF.
### Option 1: Using Docker
* __Pro__: Will definitely run regardless of your system parameters.
* __Con__: Requires rebuilding a docker image __every time you need to change the input__ (tiny code).\
You'll need to have [docker](https://www.docker.com/) on your device to build and run the solution.

The steps you'll need to take:
1. Place your input (_Tiny_ code file) in __./code/program.tiny__. It is important to do it before taking the next steps.
2. Navigate to this project folder with your terminal and run:\
``docker build -t tiny .``\
Docker will create an image based on a dockerfile that's already included.
3. When the image is created, simply run ``docker run tiny``\
Any errors or warnings will be displayed in the terminal.

If you want to run the solution with a different input (another Tiny program), you have to repeat everything from step 1. Rebuilding docker image is necessary because Docker doesn't allow direct references to a host's filesystem.\
For the same reason, this run option will not generate an _output.log_ file and will only report errors in the terminal.

### Option 2: Using Python Virtual Environment
* __Pro__: You'll be able to conveniently change the input.
* __Con__: You need Python installed on your system.

The steps you'll need to take:
1. Navigate to this project folder with your terminal and run:\
``python -m venv venv``\
This will create a virtual environment for this project. This will ensure the dependencies don't conflict with your system.
2. Then activate the environment:\
``venv/Scripts/activate``
3. Install dependencies into this environment. They __won't__ change your host system!\
``python -m pip install -r requirements.txt``
4. Now you can run the project:\
``python tiny.py SOURCE_FILE``\
__SOURCE_FILE__ is a path to your Tiny code file. The path can be relative or absolute. For example:
``python tiny.py ./code/valid1.tiny``

If you want to run the solution with a different input, you can just change the code in your _SOURCE_FILE_ or use another file path as a command argument.