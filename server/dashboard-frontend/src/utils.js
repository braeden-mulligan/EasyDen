export const equal = function(obj_1, obj_2) {
	function is_object(obj) {
  		return obj != null && typeof obj === 'object';
	}

	const keys_1 = Object.keys(obj_1);
	const keys_2 = Object.keys(obj_2);
	if (keys_1.length !== keys_2.length) return false;

	for (const key of keys_1) {
		const val_1 = obj_1[key];
		const val_2 = obj_2[key];
		const are_objects = is_object(val_1) && is_object(val_2);

		if (are_objects && !equal(val_1, val_2) || !are_objects && val_1 !== val_2) {
			return false;
		}
	}

	return true;
}

export function capitalize(input) {
    if (typeof input === "string") {
        return input.charAt(0).toUpperCase() + input.slice(1);
    } else if (Array.isArray(input)) {
        return input.map(word => word.charAt(0).toUpperCase() + word.slice(1));
    } 

	throw new TypeError("Input must be a string or an array of strings");
}
