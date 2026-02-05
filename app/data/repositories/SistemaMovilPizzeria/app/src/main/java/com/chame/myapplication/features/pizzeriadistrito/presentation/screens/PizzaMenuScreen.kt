package com.chame.myapplication.features.pizzeriadistrito.presentation.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.chame.myapplication.features.pizzeriadistrito.presentation.components.PizzaCard
import com.chame.myapplication.features.pizzeriadistrito.presentation.viewModel.PizzaViewModel
import com.chame.myapplication.features.pizzeriadistrito.presentation.viewModel.PizzaViewModelFactory

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PizzaMenuScreen(
    viewModelFactory: PizzaViewModelFactory,
    onPizzaClick: (String, Double) -> Unit,
    onHistoryClick: () -> Unit // <--- ESTA LÍNEA ES LA QUE TE FALTA AHORITA
){
    val viewModel : PizzaViewModel = viewModel(factory = viewModelFactory)
    val menuState by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            CenterAlignedTopAppBar(
                title = { Text("Menu Pizzeria", fontWeight = FontWeight.ExtraBold) },
                actions = {
                    // Botón del Historial (Arriba a la derecha)
                    IconButton(onClick = onHistoryClick) {
                        Icon(Icons.Default.DateRange, contentDescription = "Historial")
                    }
                }
            )
        }
    ) { contentPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(contentPadding)
        ) {
            when {
                menuState.isLoading -> {
                    CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
                }
                menuState.error != null -> {
                    Text(
                        text = menuState.error ?: "Error",
                        modifier = Modifier.align(Alignment.Center),
                        color = Color.Red
                    )
                }
                else -> {
                    LazyColumn(
                        modifier = Modifier.fillMaxSize(),
                        contentPadding = PaddingValues(8.dp)
                    ) {
                        items(menuState.pizzas) { pizzaItem ->
                            PizzaCard(
                                name = pizzaItem.name,
                                price = pizzaItem.price,
                                imageUrl = pizzaItem.imagenUrl,
                                modifier = Modifier.clickable {
                                    onPizzaClick(pizzaItem.name, pizzaItem.price)
                                }
                            )
                        }
                    }
                }
            }
        }
    }
}