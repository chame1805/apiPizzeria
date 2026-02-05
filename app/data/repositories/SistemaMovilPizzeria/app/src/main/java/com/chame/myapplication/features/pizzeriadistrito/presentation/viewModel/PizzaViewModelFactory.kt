package com.chame.myapplication.features.pizzeriadistrito.presentation.viewModel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import com.chame.myapplication.features.pizzeriadistrito.domain.usecases.GetPizzasUseCase

class PizzaViewModelFactory(
    private val getPizzasUseCase: GetPizzasUseCase
) : ViewModelProvider.Factory {
    override fun <T : ViewModel> create(modelClass: Class<T>) : T {
        if (modelClass.isAssignableFrom(PizzaViewModel::class.java)){
            @Suppress("UNCHECKED_CAST")
            return PizzaViewModel(getPizzasUseCase) as T
        }
        throw IllegalArgumentException("Unknown ViewModel class: ${modelClass.name}")
    }

    }
