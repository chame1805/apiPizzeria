#!/bin/bash
# ============================================================
#  Script de pruebas completo para Pizzería API
#  Uso: bash test_api.sh
# ============================================================

BASE="http://localhost:8000"
PASS="\033[0;32m[OK]\033[0m"
FAIL="\033[0;31m[FAIL]\033[0m"

sep() { echo -e "\n\033[1;34m===== $1 =====\033[0m"; }

# ─────────────────────────────────────────────
sep "1. MENÚ PÚBLICO (sin token)"
# ─────────────────────────────────────────────

echo -e "\n→ GET /menu"
curl -s "$BASE/menu" | python3 -m json.tool

echo -e "\n→ GET /productos/"
curl -s "$BASE/productos/" | python3 -m json.tool

# ─────────────────────────────────────────────
sep "2. AUTH — Registro"
# ─────────────────────────────────────────────

echo -e "\n→ POST /auth/register"
curl -s -X POST "$BASE/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_mesero@pizza.com",
    "name": "Mesero Test",
    "password": "123456",
    "rol": "MESERO"
  }' | python3 -m json.tool

# ─────────────────────────────────────────────
sep "3. AUTH — Login y captura de TOKEN"
# ─────────────────────────────────────────────

echo -e "\n→ POST /auth/login"
RESPONSE=$(curl -s -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_mesero@pizza.com",
    "password": "123456"
  }')

echo "$RESPONSE" | python3 -m json.tool

TOKEN=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
USER_ID=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['usuario']['id'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo -e "$FAIL No se pudo obtener el token. Verifica que el usuario exista."
  exit 1
else
  echo -e "\n$PASS Token capturado. User ID: $USER_ID"
fi

# ─────────────────────────────────────────────
sep "4. PRODUCTOS (requiere token ADMIN para escribir)"
# ─────────────────────────────────────────────

echo -e "\n→ GET /productos/{id} (producto 1)"
curl -s "$BASE/productos/1" | python3 -m json.tool

# Crear producto (solo funciona si el usuario es ADMIN)
echo -e "\n→ POST /productos/ (solo ADMIN)"
curl -s -X POST "$BASE/productos/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "nombre": "Pizza Prueba",
    "descripcion": "Pizza de prueba desde script",
    "precio": 12.99,
    "disponible": true
  }' | python3 -m json.tool

# ─────────────────────────────────────────────
sep "5. ÓRDENES (mesero → cocina)"
# ─────────────────────────────────────────────

echo -e "\n→ POST /orders/ — Crear nueva orden"
ORDER_RESPONSE=$(curl -s -X POST "$BASE/orders/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{
    \"pizza_name\": \"Pepperoni\",
    \"price\": 139.0,
    \"client_name\": \"Cliente Test\",
    \"total_paid\": 200.0,
    \"change_returned\": 61.0,
    \"table_number\": 5,
    \"waiter_id\": $USER_ID
  }")

echo "$ORDER_RESPONSE" | python3 -m json.tool

ORDER_ID=$(echo "$ORDER_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -n "$ORDER_ID" ]; then
  echo -e "\n$PASS Orden creada con ID: $ORDER_ID"
fi

echo -e "\n→ GET /orders/ — Ver órdenes activas (cocina)"
curl -s "$BASE/orders/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

if [ -n "$ORDER_ID" ]; then
  echo -e "\n→ PATCH /orders/$ORDER_ID/status/ — Cambiar a IN_PROGRESS"
  curl -s -X PATCH "$BASE/orders/$ORDER_ID/status/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"status": "IN_PROGRESS"}' | python3 -m json.tool

  echo -e "\n→ PATCH /orders/$ORDER_ID/status/ — Cambiar a COMPLETED"
  curl -s -X PATCH "$BASE/orders/$ORDER_ID/status/" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d '{"status": "COMPLETED"}' | python3 -m json.tool
fi

echo -e "\n→ GET /orders/$USER_ID/completed/ — Órdenes completadas del mesero"
curl -s "$BASE/orders/$USER_ID/completed/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# ─────────────────────────────────────────────
sep "6. PERFIL DEL MESERO"
# ─────────────────────────────────────────────

echo -e "\n→ GET /waiters/$USER_ID/profile/"
curl -s "$BASE/waiters/$USER_ID/profile/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

echo -e "\n→ PATCH /waiters/$USER_ID/profile/ — Actualizar nombre y teléfono"
curl -s -X PATCH "$BASE/waiters/$USER_ID/profile/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "Mesero Actualizado", "phone": "0987654321"}' | python3 -m json.tool

# ─────────────────────────────────────────────
sep "7. VENTAS / HISTORIAL (/ordenes)"
# ─────────────────────────────────────────────

echo -e "\n→ GET /ordenes/historial"
curl -s "$BASE/ordenes/historial" | python3 -m json.tool

# ─────────────────────────────────────────────
sep "8. ERROR ESPERADO — Login con credenciales incorrectas"
# ─────────────────────────────────────────────

echo -e "\n→ POST /auth/login (contraseña incorrecta — debe devolver 401)"
curl -s -o /dev/null -w "Status HTTP: %{http_code}\n" \
  -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test_mesero@pizza.com","password":"MALA"}'

echo -e "\n→ GET /orders/ sin token (debe devolver 401/403)"
curl -s -o /dev/null -w "Status HTTP: %{http_code}\n" \
  "$BASE/orders/"

# ─────────────────────────────────────────────
sep "PRUEBAS FINALIZADAS"
echo -e "\nToken usado: $TOKEN\n"
