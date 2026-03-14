from domain.greeting_service import GreetingService, FarewellService

class GreetingUseCase:
    def execute(self,name):
        service=GreetingService()
        return service.greet(name)

class FarewellUseCase:
    def execute(self,name):
        service=FarewellService()
        return service.say_goodbye(name)