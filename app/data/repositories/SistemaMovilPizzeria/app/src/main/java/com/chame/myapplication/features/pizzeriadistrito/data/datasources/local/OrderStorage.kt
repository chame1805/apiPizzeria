package com.chame.myapplication.features.pizzeriadistrito.data.datasources.local


import androidx.compose.runtime.mutableStateListOf
// Importamos la entidad de dominio
import com.chame.myapplication.features.pizzeriadistrito.domain.entities.Order

object OrderStorage {
    // Lista observable para guardar los pedidos en memoria
    val orders = mutableStateListOf<Order>()

    fun addOrder(order: Order) {
        orders.add(0, order)
    }
}