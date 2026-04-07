# 🔐 BB84 Quantum Key Distribution Simulator

A visually rich and interactive **Python-based simulation** of the **BB84 Protocol**, the first quantum cryptography protocol proposed by **Charles H. Bennett** and **Gilles Brassard** in 1984.

This project demonstrates how secure keys can be generated using the principles of **Quantum Mechanics**, and how eavesdropping can be detected through **QBER (Quantum Bit Error Rate)**.

---

## 🚀 Features

* ⚛️ Full BB84 protocol simulation
* 🎨 Colorful and readable terminal output (ANSI styled)
* 👤 Simulates **Alice**, **Bob**, and optional **Eve (attacker)**
* 🔍 Qubit-level visualization table
* 📊 QBER (Quantum Bit Error Rate) calculation
* 🔐 Automatic key acceptance/rejection decision
* 🧪 Demonstrates real-world quantum security principles

---

## 🧠 How It Works

The simulation follows the standard BB84 workflow:

1. **Alice prepares qubits**

   * Generates random bits
   * Chooses random bases (`+` or `×`)
   * Encodes photons using polarization

2. **(Optional) Eve intercepts**

   * Measures qubits randomly
   * Re-sends them → introduces errors

3. **Bob measures qubits**

   * Uses random bases
   * Gets measurement results

4. **Sifting**

   * Alice & Bob compare bases
   * Keep only matching positions

5. **QBER Estimation**

   * Random subset of bits is compared
   * Error rate is calculated

6. **Decision**

   * If QBER < threshold → ✅ Secure key
   * Else → ❌ Abort (eavesdropping suspected)

---

## 📦 Requirements

* Python 3.8+
* No external libraries required (uses only standard library)

---

## ▶️ Usage

### Run the simulation

```bash
python bb84_qkd.py
```

### Optional arguments

```bash
python bb84_qkd.py [number_of_qubits] [--eve]
```

### Examples

```bash
# Default run (128 qubits)
python bb84_qkd.py

# Custom qubits
python bb84_qkd.py 64

# Simulate attack
python bb84_qkd.py 128 --eve
```

---

## 📊 Sample Output

* Colored protocol steps
* Qubit comparison table
* QBER calculation
* Final key (hex format)
* Security decision summary

---

## 🔐 Key Concepts

* **Quantum Superposition**
* **Measurement Disturbance**
* **No-Cloning Theorem**
* **Quantum Bit Error Rate (QBER)**

These principles ensure that **any eavesdropping attempt introduces detectable errors**.

---

## 🧪 Example Scenarios

| Scenario | Expected Result           |
| -------- | ------------------------- |
| No Eve   | ✅ Low QBER, key accepted  |
| With Eve | ❌ High QBER, key rejected |

---

## 📁 Project Structure

```
bb84_qkd.py     # Main simulation script
README.md       # Project documentation
```

---

## 🎯 Learning Outcomes

This project helps you understand:

* Fundamentals of **Quantum Cryptography**
* How secure keys are generated without classical encryption
* Why quantum communication is inherently secure
* Practical implementation of BB84 in Python

---

## ⚠️ Disclaimer

This is a **simulation for educational purposes only**.
It does NOT implement a real quantum communication system.

---

## 💡 Future Improvements

* GUI version (Tkinter / Web-based)
* Real-time plotting of QBER
* Noise simulation (realistic quantum channel)
* Integration with quantum frameworks like Qiskit

---

## 👨‍💻 Author

**Mohd Feroz Khan**
(Cybersecurity Enthusiast & Quantum Tech Learner)

---

## ⭐ Support

If you found this project helpful:

* ⭐ Star the repository
* 🍴 Fork it
* 🧠 Share with others learning quantum cryptography
