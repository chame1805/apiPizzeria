package com.chame.myapplication.core.di

import android.content.Context
import com.chame.myapplication.core.network.PizzeriaApi
import com.chame.myapplication.features.pizzeriadistrito.data.repositories.PizzaRepositoryImpl
import com.chame.myapplication.features.pizzeriadistrito.domain.repositories.PizzaRepository
// --- ESTAS SON LAS IMPORTACIONES QUE TE FALTABAN ---
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class AppContainer(context: Context) {
    private val _retrofit = Retrofit.Builder()
        // Usa 10.0.2.2 si estás en el emulador de Android Studio
        .baseUrl("http://10.0.2.2:8000/")
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    val pizzeriaApi : PizzeriaApi by lazy {
        _retrofit.create(PizzeriaApi::class.java)
    }

    val pizzaRepository : PizzaRepository by lazy {
        PizzaRepositoryImpl(pizzeriaApi)
    }
}