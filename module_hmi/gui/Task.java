package gui;

public class Task {

	private int index;
	private String name;
	private String description;
	private int maxIndex;

	/**
	 * Constructor
	 * 
	 * @param name The name of the task
	 * @param descr The description of the task
	 */
	public Task(int index, String name, String descr, int maxIndex) {
		setIndex(index);
		setName(name);
		setDescription(descr);
		setMaxIndex(maxIndex);
	}

	// Getters/Setters
	/**
	 * @return the index
	 */
	public int getIndex() {
		return index;
	}

	/**
	 * @param index the index to set
	 */
	public void setIndex(int index) {
		this.index = index;
	}

	/**
	 * @return the name
	 */
	public String getName() {
		return name;
	}

	/**
	 * @param name the name to set
	 */
	public void setName(String name) {
		this.name = name;
	}

	/**
	 * @return the description
	 */
	public String getDescription() {
		return description;
	}

	/**
	 * @param description the description to set
	 */
	public void setDescription(String description) {
		this.description = description;
	}

	/**
	 * @return the maxIndex
	 */
	public int getMaxIndex() {
		return maxIndex;
	}

	/**
	 * @param maxIndex the maxIndex to set
	 */
	public void setMaxIndex(int maxIndex) {
		this.maxIndex = maxIndex;
	}

}
