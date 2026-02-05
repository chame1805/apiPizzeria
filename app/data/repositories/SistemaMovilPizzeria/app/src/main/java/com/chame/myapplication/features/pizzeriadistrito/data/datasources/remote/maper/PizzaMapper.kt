package com.chame.myapplication.features.pizzeriadistrito.data.datasources.remote.maper

import com.chame.myapplication.features.pizzeriadistrito.data.datasources.remote.model.PizzaDto
import com.chame.myapplication.features.pizzeriadistrito.domain.entities.Pizzas

fun PizzaDto.toDomain(): Pizzas {
    return Pizzas(
        id = this.id,
        name = this.nombre,
        price = this.precio,
        imagenUrl = "https://cdn-icons-png.flaticon.com/512/3595/3595458.png"

    )
}