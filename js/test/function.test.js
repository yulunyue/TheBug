import Fun from '../src/function';
test('fun.list', () => {
    expect(Fun.list(3)).toStrictEqual([0, 1, 2]);
});
test('fun.extend', () => {
    let a = {
        _a: 0,
        c() {
            return 0
        }
    }
    let b = {
        _a: 1,
        c() {
            return 1
        }
    }
    let c = Fun.extend(a, b)
    expect(c.c()).toEqual(1);
});