package com.chame.myapplication.features.pizzeriadistrito.presentation.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OrderScreen(
    pizzaName: String,
    pizzaPrice: Double,
    onBackClick: () -> Unit,
    // Callback que devuelve los datos al Main
    onPayClick: (String, Double, Double) -> Unit
) {
    var clientName by remember { mutableStateOf("") }
    var address by remember { mutableStateOf("") }
    var amountPaidText by remember { mutableStateOf("") }

    val amountPaid = amountPaidText.toDoubleOrNull() ?: 0.0
    val change = amountPaid - pizzaPrice
    val isPaymentSufficient = amountPaid >= pizzaPrice

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Orden: $pizzaName") },
                navigationIcon = {
                    IconButton(onClick = onBackClick) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Atrás")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier.padding(padding).padding(16.dp).fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("Total: $$pizzaPrice", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)

            Spacer(modifier = Modifier.height(16.dp))
            OutlinedTextField(value = clientName, onValueChange = { clientName = it }, label = { Text("Nombre Cliente") }, modifier = Modifier.fillMaxWidth())

            Spacer(modifier = Modifier.height(8.dp))
            OutlinedTextField(value = address, onValueChange = { address = it }, label = { Text("Dirección") }, modifier = Modifier.fillMaxWidth())

            Spacer(modifier = Modifier.height(8.dp))
            OutlinedTextField(
                value = amountPaidText,
                onValueChange = { if (it.all { c -> c.isDigit() || c == '.' }) amountPaidText = it },
                label = { Text("¿Con cuánto paga?") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                modifier = Modifier.fillMaxWidth(),
                prefix = { Text("$") }
            )

            Spacer(modifier = Modifier.height(16.dp))
            if (amountPaidText.isNotEmpty()) {
                Text(
                    text = if (isPaymentSufficient) "Cambio: $${String.format(Locale.US, "%.2f", change)}" else "Falta: $${String.format(Locale.US, "%.2f", -change)}",
                    color = if (isPaymentSufficient) Color(0xFF4CAF50) else Color.Red,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(24.dp))
            Button(
                onClick = { onPayClick(clientName, amountPaid, change) },
                enabled = clientName.isNotEmpty() && address.isNotEmpty() && isPaymentSufficient,
                modifier = Modifier.fillMaxWidth().height(50.dp)
            ) {
                Text("CONFIRMAR PAGO")
            }
        }
    }
}