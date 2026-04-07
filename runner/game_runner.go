// TODO package desccription
package cgolrunner

import "fmt"

// Coord structs are used as map keys containing the XY coordinates for the uint64 word chunks
type Coord struct {
	X, Y int
}

// These two maps each represent the infinite 2D plane, which is made up of 1x64 horizontal rows of cells called chunks.
// Each chunk has a Coord as a key and a uint64 word as a value.
// The bits in each word represent the individual states of the cells in that chunk.
// Only the chunks that contain live cells are stored.
var gridA, gridB map[Coord]uint64

// GridIn and GridOut use pointer swapping to minimize memory writes. Each points to either gridA or gridB.
var GridIn, GridOut *map[Coord]uint64 = &gridA, &gridB

type wordShift struct {
	// yPos is the relative y position of the neighboring chunk.
	yPos int
	// shift can be one of three functions: leftShift, rightShift, or noShift
	shift func(Coord) (uint64, Coord)
}

// leftShift returns the word at myPos shifted 1 bit to the left.
// It fills the empty bit using the leftmost bit of the chunk to the right.
// Iff this chunk is not present, the chunk's Coord is returned.
func leftShift(myPos Coord) (word uint64, newChunk Coord) {
	sideCoord := Coord{myPos.X + 1, myPos.Y}
	sideWord, exists := (*GridIn)[sideCoord]
	if !exists {
		newChunk = sideCoord
	}
	word = ((*GridIn)[myPos] << 1) | (sideWord >> 63)
	return
}

// rightShift returns the word at myPos shifted 1 bit to the right.
// It fills the empty bit using the rightmost bit of the chunk to the left.
// Iff this chunk is not present, the chunk's Coord is returned.
func rightShift(myPos Coord) (word uint64, newChunk Coord) {
	sideCoord := Coord{myPos.X - 1, myPos.Y}
	sideWord, exists := (*GridIn)[sideCoord]
	if !exists {
		newChunk = sideCoord
	}
	word = ((*GridIn)[myPos] >> 1) | (sideWord << 63)
	return
}

// noShift acts as a filler function. It simply returns the word of the chunk at myPos.
// Iff this chunk is not present, the chunk's Coord is returned.
func noShift(myPos Coord) (word uint64, newChunk Coord) {
	word, exists := (*GridIn)[myPos]
	if !exists {
		newChunk = myPos
	}
	return
}

// srndWords is a constant array, listing the relative y coordinate and bit shift function to
// be performed on the 8 surrounding neighbors.
var srndWords = [8]wordShift{
	// neighboring cells are in the following order:
	// 0 1 2
	// 3 X 4
	// 5 6 7
	{1, leftShift},   // 0
	{1, noShift},     // 1
	{1, rightShift},  // 2
	{0, leftShift},   // 3
	{0, rightShift},  // 4
	{-1, leftShift},  // 5
	{-1, noShift},    // 6
	{-1, rightShift}, // 7
}

// InitGrid sets desired initial values to the global grid variables.
func InitGrid(grid map[Coord]uint64) {
	*GridIn = grid
	*GridOut = make(map[Coord]uint64)
}

// SwapGrids performs a pointer swap, then clears *GridOut.
func SwapGrids() {
	GridIn, GridOut = GridOut, GridIn
	*GridOut = make(map[Coord]uint64)
}

// NextGen reads *GridIn and writes the next generation to *GridOut
func NextGen() {
	// checkLater is a set of the Coords of all empty chunks bordering live chunks. These will be iterated over later to check for changes.
	var checkLater = make(map[Coord]struct{}) // DEV note: change to global scope for efficient memory?

	// Iterate over live chunks. p means position and w means word.
	for p, w := range *GridIn {
		// These vars make up a parallel register for counting the neighbors of each cell in w. b1 is the LSB, b2 next, and b3 the MSB.
		var b1, b2, b3 uint64

		// Iterate over neighbors of this chunk.
		for _, nInfo := range srndWords {
			// Get new shifted word of neighbor and its potentially unexistent neighboring chunk.
			nw, missing := nInfo.shift(Coord{p.X, p.Y + nInfo.yPos})

			// Add Coord of neighboring chunk to checkLater if nonexistent.
			if missing != (Coord{}) {
				checkLater[missing] = struct{}{} // TODO optimize how the neighbor chunk is stored so it isn't called twice?
			}

			// add nw to the registers
			b3 = b3 ^ (b2 & b1 & nw)
			b2 = b2 ^ (b1 & nw)
			b1 = b1 ^ nw
			fmt.Print()
		}
		// Apply Game Of Life rule (B3/S23) to neighbor count.
		outputWord := (b1 | w) & b2 & ^b3
		if outputWord != 0 {
			(*GridOut)[p] = outputWord
		}
	}

	// Iterate over dead chunks in checkLater. Note that this code is largely a copy of the loop above.
	for p := range checkLater {
		// These vars make up a parallel register for counting the neighbors of each cell in w. b1 is the LSB, b2 next, and b3 the MSB.
		var b1, b2, b3 uint64

		// Iterate over neighbors of this chunk.
		for _, nInfo := range srndWords {
			// Get new shifted word of neighbor.
			nw, _ := nInfo.shift(Coord{p.X, p.Y + nInfo.yPos})

			// add nw to the registers
			b3 = b3 ^ (b2 & b1 & nw)
			b2 = b2 ^ (b1 & nw)
			b1 = b1 ^ nw

		}
		// Apply Game Of Life rule (B3/S23) to neighbor count.
		outputWord := b1 & b2 & ^b3
		if outputWord != 0 {
			(*GridOut)[p] = outputWord
		}
	}
}
