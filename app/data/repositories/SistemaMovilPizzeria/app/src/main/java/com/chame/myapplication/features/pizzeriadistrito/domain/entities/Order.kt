package com.chame.myapplication.features.pizzeriadistrito.domain.entities

import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

data class Order(
    val pizzaName: String,
    val price: Double,
    val clientName: String,     // MainActivity busca este nombre
    val totalPaid: Double,
    val changeReturned: Double, // MainActivity busca este nombre
    val date: String = SimpleDateFormat("dd/MM HH:mm", Locale.getDefault()).format(Date())
)