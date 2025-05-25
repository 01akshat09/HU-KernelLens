package main

import (
	"fmt"
	"math"
	"math/rand"
	"net/http"
	"strconv"
	"time"
)

func fib(n int) int {
	if n <= 1 {
		return n
	}
	return fib(n-1) + fib(n-2)
}

func fibHandler(w http.ResponseWriter, r *http.Request) {
	n := parseQueryParam(r, "n", 35)
	start := time.Now()
	result := fib(n)
	duration := time.Since(start)
	fmt.Fprintf(w, "Fibonacci(%d) = %d (took %s)\n", n, result, duration)
}

func primeHandler(w http.ResponseWriter, r *http.Request) {
	n := parseQueryParam(r, "n", 100000)
	start := time.Now()
	count := 0
	for i := 2; i < n; i++ {
		isPrime := true
		for j := 2; j <= int(math.Sqrt(float64(i))); j++ {
			if i%j == 0 {
				isPrime = false
				break
			}
		}
		if isPrime {
			count++
		}
	}
	duration := time.Since(start)
	fmt.Fprintf(w, "Found %d prime numbers < %d (took %s)\n", count, n, duration)
}

func sortHandler(w http.ResponseWriter, r *http.Request) {
	n := parseQueryParam(r, "n", 100000)
	arr := make([]int, n)
	for i := range arr {
		arr[i] = rand.Intn(n)
	}
	start := time.Now()
	quickSort(arr)
	duration := time.Since(start)
	fmt.Fprintf(w, "Sorted %d numbers (took %s)\n", n, duration)
}

func quickSort(a []int) {
	if len(a) < 2 {
		return
	}
	left, right := 0, len(a)-1
	pivot := rand.Intn(len(a))
	a[pivot], a[right] = a[right], a[pivot]
	for i := range a {
		if a[i] < a[right] {
			a[i], a[left] = a[left], a[i]
			left++
		}
	}
	a[left], a[right] = a[right], a[left]
	quickSort(a[:left])
	quickSort(a[left+1:])
}

func matrixHandler(w http.ResponseWriter, r *http.Request) {
	n := parseQueryParam(r, "n", 200)
	A := make([][]int, n)
	B := make([][]int, n)
	C := make([][]int, n)
	for i := range A {
		A[i] = make([]int, n)
		B[i] = make([]int, n)
		C[i] = make([]int, n)
		for j := 0; j < n; j++ {
			A[i][j] = rand.Intn(100)
			B[i][j] = rand.Intn(100)
		}
	}
	start := time.Now()
	for i := 0; i < n; i++ {
		for j := 0; j < n; j++ {
			sum := 0
			for k := 0; k < n; k++ {
				sum += A[i][k] * B[k][j]
			}
			C[i][j] = sum
		}
	}
	duration := time.Since(start)
	fmt.Fprintf(w, "Multiplied two %dx%d matrices (took %s)\n", n, n, duration)
}

func parseQueryParam(r *http.Request, key string, defaultVal int) int {
	valStr := r.URL.Query().Get(key)
	val, err := strconv.Atoi(valStr)
	if err != nil || val <= 0 {
		return defaultVal
	}
	return val
}

func main() {
	rand.Seed(time.Now().UnixNano())

	http.HandleFunc("/fib", fibHandler)
	http.HandleFunc("/prime", primeHandler)
	http.HandleFunc("/sort", sortHandler)
	http.HandleFunc("/matrix", matrixHandler)

	fmt.Println("CPULoadHub running at http://localhost:8080")
	fmt.Println("Try /fib?n=35, /prime?n=50000, /sort?n=50000, /matrix?n=150")

	if err := http.ListenAndServe(":8080", nil); err != nil {
		fmt.Println("Error starting server:", err)
	}
}