Tea.context(function () {
	this.minGB = ""
	this.minSize = ""

	this.maxGB = ""
	this.maxSize = ""

	this.$delay(function () {
		let that = this
		this.$watch("minGB", function (v) {
			v = parseInt(v)
			if (isNaN(v) || v <= 0) {
				that.minSize = ""
			} else {
				that.minSize = teaweb.formatBytes(v * Math.pow(1024, 3))
			}
		})
		this.$watch("maxGB", function (v) {
			v = parseInt(v)
			if (isNaN(v) || v < 0) {
				that.maxSize = ""
			} else if (v == 0) {
				that.maxSize = "∞"
			} else {
				that.maxSize = teaweb.formatBytes(v * Math.pow(1024, 3))
			}
		})
	})
})