# Parser and Type System for Tiny
This project contains a parser and a type system for a made-up language called **Tiny**.\
It parses the code using a grammar and checks for basic syntax and type errors as well as local scope overflows.

You can checkout the repo directly: https://github.com/NitricCS/tiny-project.git

The project uses a SLY-based symbol table project as a base: https://github.com/NitricCS/symbol-table-sly

### Installation
You'll need to have docker on your device to build and run the solution.

Once you have docker up and running, navigate to this project folder with your terminal and run:\
``docker build -t tiny .``\
Docker will create an image based on a dockerfile in this project. This will omit potential dependencies conflicts, although this project doesn't have a lot of them.

### Usage
The input file with the Tiny code should be placed into _./code/program.tiny_.\
Unfortunately, docker doesn't allow simple references to the host filesystem, thus, the input file has to have a fixed location.

When the image is created, simply run ``docker run tiny``\
Any errors or warnings will be displayed in the terminal.\
Additionally, an __output.log__ file will be created. It will contain symbol table scopes and a variable resolution table.

### Documentation
* [Main logic](./docs/main_logic.md)
* [Lexer](./docs/lexer.md)
* [Type system methods](./docs/typing.md)
* [Logger](./docs/logger.md)