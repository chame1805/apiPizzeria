package com.chame.myapplication.features.pizzeriadistrito.domain.entities

data class Pizzas (
    val id: Int,
    val name: String,
    val price: Double,
     val imagenUrl: String? = null
)