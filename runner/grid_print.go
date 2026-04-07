package cgolrunner

import (
	"fmt"
	"strings"
)

// Prints grid within specified bounds. bR is exclusive.
func PrintChunkWindow(grid *map[Coord]uint64, tL Coord, bR Coord) {
	// TODO raise error if tL and bR conflict
	var out string = "grid:\n"
	for y := tL.Y; y > bR.Y; y-- { // moves downward
		for x := tL.X; x < bR.X; x++ { // moves to the right
			out += fmt.Sprintf("%064b", (*grid)[Coord{x, y}])
		}
		out += "\n"
	}

	out = strings.ReplaceAll(out, "0", ".")
	out = strings.ReplaceAll(out, "1", "*")
	fmt.Print(out)
}

// TODO func PrintCellWindow
