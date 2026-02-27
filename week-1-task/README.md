####GET_API Using Hexagonal Architecture 

This projectc implements a simple GET API that provides Greeting and Farewell messages. 
It's structured using Hexagonal architecture which provide seperate core business logic, application use cases and interface adapters.

##Project Structure 
week-1 task/
├── domain/          # Core business logic
│   └── greeting_service.py  
├── application/     # Application layer (Port) 
│   └── greeting_use_case.py 
├── myproject/views.py    # Adapter 
├── manage.py       
└── db.sqlite3      

## *Architecture*

* *Domain Layer:*
  Contains methods GreetingService and FarewellService — core business logic that generates messages.

* *Application Layer:*
  Contains GreetingUseCase and FarewellUseCase — uses core services to get greeting or farewell messages.

* *Interface/Adapter Layer:*
  Django views convert HTTP requests to application calls and return JSON responses.
