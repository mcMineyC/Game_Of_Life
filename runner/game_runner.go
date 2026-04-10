// Package cgolrunner is a program for computing Conway's Game of Life using bitwise parallel addition.
//
// The game grid is divided into 1x64 horizontal rows of cells called chunks.
// The grid is stored as type map[Coord]uint64. Each bit of the uint64 word represents the
// state of each cell in the chunk. Only chunks with live cells are stored in the map.
//
// This package also contains functions to print the grid and convert its data to rle.
package cgolrunner

// Coord structs are used as map keys containing the XY coordinates for the uint64 word chunks
type Coord struct {
	X, Y int
}

// These two maps each represent the infinite 2D plane, which is made up of 1x64 horizontal rows of cells called chunks.
// Each chunk has a Coord as a key and a uint64 word as a value.
// The bits in each word represent the individual states of the cells in that chunk.
// Only the chunks that contain live cells are stored.
var gridA, gridB map[Coord]uint64

// The NextGen function reads from GridIn and writes to GridOut.
// Pointer swapping is used between generations via SwapGrids() to minimize memory writes.
var GridIn, GridOut *map[Coord]uint64 = &gridA, &gridB

// wordShift contains instructions to get the neighboring chunk and bit shift it as necessary.
type wordShift struct {
	// yPos is the relative y position of the neighboring chunk.
	yPos int
	// shift can be one of three functions: leftShift, rightShift, or noShift
	shift func(Coord) (uint64, Coord)
}

// leftShift does two things: (1) It returns the word at myPos shifted 1 bit to the left.
// (2) It returns the Coord of the chunk on the right if this chunk doesn't exist.
func leftShift(myPos Coord) (word uint64, newChunk Coord) {
	sideCoord := Coord{myPos.X + 1, myPos.Y} // Get the Coord of chunk on the right.
	sideWord, exists := (*GridIn)[sideCoord] // Get the word of this chunk and it's existence state.
	if !exists {                             // Return the sideCoord value if the chunk doesn't exist.
		newChunk = sideCoord
	}
	word = ((*GridIn)[myPos] << 1) | (sideWord >> 63) // Bit-shift the word at myPos 1 to the left, and include the leftmost bit of the right chunk.
	return
}

// rightShift does two things: (1) It returns the word at myPos shifted 1 bit to the right.
// (2) It returns the Coord of the chunk on the left if this chunk doesn't exist.
func rightShift(myPos Coord) (word uint64, newChunk Coord) {
	sideCoord := Coord{myPos.X - 1, myPos.Y} // Get the Coord of chunk on the left.
	sideWord, exists := (*GridIn)[sideCoord] // Get the word of this chunk and it's existence state.
	if !exists {                             // Return the sideCoord value if the chunk doesn't exist.
		newChunk = sideCoord
	}
	word = ((*GridIn)[myPos] >> 1) | (sideWord << 63) // Bit-shift the word at myPos 1 to the right, and include the rightmost bit of the left chunk.
	return
}

// leftShift does two things: (1) It returns the word at myPos (without shifting).
// (2) It returns myPos if the chunk doesn't exist.
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

// SwapGrids performs a pointer swap on the grids, then clears *GridOut.
func SwapGrids() {
	GridIn, GridOut = GridOut, GridIn
	*GridOut = make(map[Coord]uint64)
}

// NextGen reads from *GridIn and writes the next generation to *GridOut
func NextGen() {
	// checkLater is a set of the Coords of all empty chunks bordering live chunks. These will be iterated over later to check for changes.
	var checkLater = make(map[Coord]struct{})

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
				checkLater[missing] = struct{}{}
			}

			// add nw to the parallel register
			b3 = b3 ^ (b2 & b1 & nw)
			b2 = b2 ^ (b1 & nw)
			b1 = b1 ^ nw
		}
		// Apply Game Of Life rule (B3/S23) to neighbor count.
		outputWord := (b1 | w) & b2 & ^b3
		if outputWord != 0 { // adds to *GridOut if it contains live cells
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

			// add nw to the parallel register
			b3 = b3 ^ (b2 & b1 & nw)
			b2 = b2 ^ (b1 & nw)
			b1 = b1 ^ nw

		}
		// Apply Game Of Life rule (B3/S23) to neighbor count.
		outputWord := b1 & b2 & ^b3
		if outputWord != 0 { // adds to *GridOut if it contains live cells
			(*GridOut)[p] = outputWord
		}
	}
}

// TODO don't add corner neighbors to checkLater
