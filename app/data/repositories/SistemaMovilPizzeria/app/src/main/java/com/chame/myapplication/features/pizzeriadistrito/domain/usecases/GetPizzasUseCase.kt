package com.chame.myapplication.features.pizzeriadistrito.domain.usecases

import com.chame.myapplication.features.pizzeriadistrito.domain.entities.Pizzas
import com.chame.myapplication.features.pizzeriadistrito.domain.repositories.PizzaRepository

class GetPizzasUseCase (
    private val repository: PizzaRepository
){
    suspend operator fun invoke(): Result<List<Pizzas>>{
        return try {
            val pizzas = repository.getPizzas()
            val filteredPizzas = pizzas.filter { it.price > 0}
            if (filteredPizzas.isEmpty()){
                Result.failure(Exception("No se encontraron pizzas disponibles"))
            }else{
                Result.success(filteredPizzas)
            }
        }catch (e: Exception){
            Result.failure(e)
        }
    }
}