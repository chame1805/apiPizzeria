package com.chame.myapplication.core.network

import com.chame.myapplication.features.pizzeriadistrito.data.datasources.remote.model.PizzaDto
import retrofit2.http.GET

interface PizzeriaApi {
    @GET("menu")
    suspend fun getMenu(): List<PizzaDto>
}