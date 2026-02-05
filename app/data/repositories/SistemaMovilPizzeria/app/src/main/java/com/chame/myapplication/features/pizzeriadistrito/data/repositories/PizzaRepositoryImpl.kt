package com.chame.myapplication.features.pizzeriadistrito.data.repositories

import com.chame.myapplication.core.network.PizzeriaApi
import com.chame.myapplication.features.pizzeriadistrito.data.datasources.remote.maper.toDomain
import com.chame.myapplication.features.pizzeriadistrito.domain.entities.Pizzas
import com.chame.myapplication.features.pizzeriadistrito.domain.repositories.PizzaRepository

class PizzaRepositoryImpl (
    private val _api : PizzeriaApi
) : PizzaRepository {
    override suspend fun getPizzas() : List<Pizzas> {
        val response = _api.getMenu()
        return response.map { it.toDomain() }
    }
}