from pynes.types import uint16


class Uint16Spec:
    def test_uint16_constant_assign(self):
        var_big = uint16()
        var_big = 300

        self.assertEqual(var_big, 300)

    def test_uint16_add_constant(self):
        var_big = uint16()
        var_big = 300
        var_big += 500

        self.assertEqual(var_big, 800)

    def test_uint16_add_carry(self):
        var_big = uint16()
        var_big = 255
        var_big += 1

        self.assertEqual(var_big, 256)

    def test_uint16_sub_constant(self):
        var_big = uint16()
        var_big = 300
        var_big -= 44

        self.assertEqual(var_big, 256)

    def test_uint16_add_uint8_var(self):
        var_big = uint16()
        var_big = 250
        var_n = 10
        var_big += var_n

        self.assertEqual(var_big, 260)

    def test_uint16_copy(self):
        var_big = uint16()
        var_other = uint16()
        var_big = 1000
        var_other = var_big

        self.assertEqual(var_other, 1000)

    def test_uint16_times_uint8(self):
        var_big = uint16()
        var_big = 1000
        var_n = 42
        var_big = var_big * var_n

        self.assertEqual(var_big, 42000)

    def test_uint16_annotation(self):
        var_big: uint16 = 400

        self.assertEqual(var_big, 400)

    def test_uint16_annotation_arithmetic(self):
        var_big: uint16 = 40000
        var_big += 320

        self.assertEqual(var_big, 40320)

    def test_uint16_annotation_without_value(self):
        var_big: uint16
        var_big = 0
        var_big = 700

        self.assertEqual(var_big, 700)

    def test_uint16_factorial_8(self):
        var_big = uint16()
        var_big = 1
        var_n = 8

        while var_n > 1:
            var_big = var_big * var_n
            var_n -= 1

        self.assertEqual(var_big, 40320)

    def test_uint16_equal_constant_true(self):
        var_big = uint16()
        var_big = 1000
        var_result = 0

        if var_big == 1000:
            var_result = 1

        self.assertEqual(var_result, 1)

    def test_uint16_equal_constant_false(self):
        var_big = uint16()
        var_big = 1000
        var_result = 0

        if var_big == 999:
            var_result = 1

        self.assertEqual(var_result, 0)

    def test_uint16_not_equal_constant_true(self):
        var_big = uint16()
        var_big = 1000
        var_result = 0

        if var_big != 999:
            var_result = 1

        self.assertEqual(var_result, 1)

    def test_uint16_not_equal_constant_false(self):
        var_big = uint16()
        var_big = 1000
        var_result = 0

        if var_big != 1000:
            var_result = 1

        self.assertEqual(var_result, 0)
