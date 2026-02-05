package com.chame.myapplication

import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.chame.myapplication.core.di.AppContainer
import com.chame.myapplication.features.pizzeriadistrito.di.PizzeriaModule
import com.chame.myapplication.ui.theme.MyApplicationTheme
// IMPORTS DE TUS PANTALLAS
import com.chame.myapplication.features.pizzeriadistrito.presentation.screens.*
// IMPORTS DE TUS DATOS (LOCAL Y DOMAIN)
import com.chame.myapplication.features.pizzeriadistrito.data.datasources.local.OrderStorage
import com.chame.myapplication.features.pizzeriadistrito.domain.entities.Order

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val appContainer = AppContainer(applicationContext)
        val pizzeriaModule = PizzeriaModule(appContainer)
        enableEdgeToEdge()

        setContent {
            MyApplicationTheme {
                val navController = rememberNavController()

                NavHost(navController = navController, startDestination = "menu") {

                    // RUTA 1: MENÚ
                    composable("menu") {
                        PizzaMenuScreen(
                            viewModelFactory = pizzeriaModule.providePizzaViewModelFactory(),
                            onPizzaClick = { name, price -> navController.navigate("order/$name/$price") },
                            onHistoryClick = { navController.navigate("history") }
                        )
                    }

                    // RUTA 2: ORDEN
                    composable(
                        route = "order/{name}/{price}",
                        arguments = listOf(
                            navArgument("name") { type = NavType.StringType },
                            navArgument("price") { type = NavType.FloatType }
                        )
                    ) { backStackEntry ->
                        val pizzaName = backStackEntry.arguments?.getString("name") ?: ""
                        val pizzaPrice = backStackEntry.arguments?.getFloat("price")?.toDouble() ?: 0.0

                        OrderScreen(
                            pizzaName = pizzaName,
                            pizzaPrice = pizzaPrice,
                            onBackClick = { navController.popBackStack() },
                            onPayClick = { client, paid, change ->
                                // AQUÍ OCURRE LA MAGIA: Guardamos en Local Datasource
                                val newOrder = Order(
                                    pizzaName = pizzaName,
                                    price = pizzaPrice,
                                    clientName = client,
                                    totalPaid = paid,
                                    changeReturned = change
                                )
                                OrderStorage.addOrder(newOrder)

                                Toast.makeText(applicationContext, "¡Venta Guardada!", Toast.LENGTH_SHORT).show()
                                navController.popBackStack()
                            }
                        )
                    }

                    // RUTA 3: HISTORIAL
                    composable("history") {
                        HistoryScreen(onBackClick = { navController.popBackStack() })
                    }
                }
            }
        }
    }
}