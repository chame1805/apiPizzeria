package com.chame.myapplication.features.pizzeriadistrito.domain.repositories
import com.chame.myapplication.features.pizzeriadistrito.domain.entities.Pizzas



interface PizzaRepository {
suspend fun getPizzas(): List<Pizzas>
}


