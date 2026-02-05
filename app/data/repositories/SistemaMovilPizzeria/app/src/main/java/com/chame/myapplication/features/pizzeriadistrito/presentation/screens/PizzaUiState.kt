package com.chame.myapplication.features.pizzeriadistrito.presentation.screens

import com.chame.myapplication.features.pizzeriadistrito.domain.entities.Pizzas

data class PizzaUiState (
    val isLoading: Boolean = false,
    val pizzas: List<Pizzas> = emptyList(),
    val error: String? = null
)