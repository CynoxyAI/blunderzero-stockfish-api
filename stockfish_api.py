from flask import Flask, request, jsonify
import chess
import chess.engine

app = Flask(__name__)

# Initialize Stockfish Engine
ENGINE_PATH = "stockfish-ubuntu-x86-64-avx2"  # Change path if needed
engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

@app.route("/", methods=["GET"])
def home():
    return "♟️ Stockfish API is running!"

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()
        fen = data.get("fen")
        
        if not fen:
            return jsonify({"error": "Missing 'fen' parameter"}), 400

        board = chess.Board(fen)
        result = engine.analyse(board, chess.engine.Limit(time=1.0))

        return jsonify({
            "best_move": result["pv"][0].uci(),
            "score": result["score"].relative.score() if result["score"].relative is not None else "N/A"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analyze", methods=["GET"])
def analyze_get():
    return jsonify({"message": "Use POST to analyze a position"}), 405  # Friendly message

@app.route("/shutdown", methods=["POST"])
def shutdown():
    """Gracefully shuts down Stockfish."""
    global engine
    engine.quit()
    return jsonify({"message": "Stockfish engine closed."})

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        engine.quit()
