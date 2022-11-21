function calculate_winner(squares) {
  const lines = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
  ];

  for (let i = 0; i < lines.length; i++) {
    const [a, b, c] = lines[i];
    if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
      return squares[a];
    }
  }

  return null;
}

//class Square extends React.Component {
//  render() {
function Square(props) {
    return (
      <button className="square" onClick={ () => props.click_back() } >
		{ props.value }
      </button>
    );
  }
//}

class Board extends React.Component {

  renderSquare(i) {
    return <Square key={i.toString()} value={this.props.squares[i]} click_back={ () => this.props.click_back(i) } />;
  }

  render() {
	let table = []
	let row = [];

	for (let i = 1; i < 10; ++i) {
		row.push(this.renderSquare(i - 1));
		if (i % 3 == 0) {
			let x = <div key={i.toString()} className="board-row">{row}</div>
			table.push(x);
			row = []
		}
	}

    return (
      <div>
		{table}
      </div>
    );
  }
}

class Game extends React.Component {
	constructor(props) {
		super(props);
		this.state = {
			history: [
				{ squares: Array(9).fill(null) }
			],
			step: 0,
			x_next: true,
		}
	}

  jump_to(step) {
    this.setState({
      step: step,
      x_next: (step % 2) === 0,
    });
  }

	handle_click(i) {
		const history = this.state.history.slice(0, this.state.step + 1);
		const current = history[history.length - 1];
		const squares = current.squares.slice();

		if (calculate_winner(squares) || squares[i]) return;

		squares[i] = this.state.x_next ? 'X' : 'O';
		this.setState({
			history: history.concat([{squares: squares}]),
			step: history.length,
			x_next: !this.state.x_next,
		});
	}

	reset_board() {
		this.setState({
			history : [
				{ squares: Array(9).fill(null) }
			],
			step: 0,
			x_next: true,
		})
	}

  render() {
	let history = this.state.history;
    let current = history[this.state.step];
	let winner = calculate_winner(current);

	const moves = history.map((step, move) => {
      const desc = move ? 'Go to move #' + move : 'Go to game start';
      return (
        <li key={move}>
          <button onClick={() => this.jump_to(move)}>{desc}</button>
        </li>
      );
    });

    let status;
	if (winner) {
		status = "Winner: " + winner;
	} else {
		status = 'Next turn: ' + (this.state.x_next ? 'X' : 'O');
	}

    return (
      <div className="game">
        <div className="game-board">
          <Board squares={ current.squares } click_back={ (i) => this.handle_click(i) } />
        </div>

        <div className="game-info">
          <div>{ status }</div>
          <ol>{ moves }</ol>
			<button className="reset" onClick={ () => this.reset_board() } > Reset </button>
        </div>
      </div>
    );
  }
}

// ========================================

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<Game />);
