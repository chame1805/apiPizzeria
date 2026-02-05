package com.chame.myapplication.features.pizzeriadistrito.di

import com.chame.myapplication.core.di.AppContainer
import com.chame.myapplication.features.pizzeriadistrito.domain.usecases.GetPizzasUseCase
import com.chame.myapplication.features.pizzeriadistrito.presentation.viewModel.PizzaViewModelFactory

class PizzeriaModule(
    private val _appContainer : AppContainer
) {
    private fun provideGetPizzasUseCase() : GetPizzasUseCase {
        return GetPizzasUseCase(_appContainer.pizzaRepository)
    }

    fun providePizzaViewModelFactory() : PizzaViewModelFactory {
        return PizzaViewModelFactory(
            getPizzasUseCase = provideGetPizzasUseCase()
        )
    }
} // <--- ¡ESTA ES LA LLAVE QUE TE FALTA!