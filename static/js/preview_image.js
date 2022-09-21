let imageSrc = null
let cible = document.getElementById('preview')
let previewValue = cible && cible.getAttribute('src')
const showPreview = (e) => {
  if (e.target.files && e.target.files[0]) {
    imageFile = e.target.files[0]
    const reader = new FileReader()
    reader.onload = (x) => {
      imageSrc = x.target.result
      cible.setAttribute('src', imageSrc)
    }
    reader.readAsDataURL(imageFile)
  } else {
    cible.setAttribute('src', previewValue)
  }
}

let source = null
let cible2 = document.getElementById('preview2')
let defaultValue = cible2 && cible2.getAttribute('src')
const PreviewImage = (e) => {
  if (e.target.files && e.target.files[0]) {
    imageFile = e.target.files[0]
    const reader = new FileReader()
    reader.onload = (x) => {
      source = x.target.result
      cible2.setAttribute('src', source)
      cible2.style.display = 'block'
    }
    reader.readAsDataURL(imageFile)
  } else {
    cible2.setAttribute('src', defaultValue)
    cible2.style.display = 'none'
  }
}

let coverSrc = null
let coverCible = document.getElementById('cover_picture')
let coverPreview = coverCible && coverCible.getAttribute('src')
const showCoverPreview = (e) => {
  if (e.target.files && e.target.files[0]) {
    imageFile = e.target.files[0]
    const reader = new FileReader()
    reader.onload = (x) => {
      coverSrc = x.target.result
      coverCible.setAttribute('src', coverSrc)
    }
    reader.readAsDataURL(imageFile)
  } else {
    coverCible.setAttribute('src', coverPreview)
  }
}

let profileSrc = null
let profileCible = document.getElementById('profile_picture')
let profileView = profileCible && profileCible.getAttribute('src')
const showProfileView = (e) => {
  if (e.target.files && e.target.files[0]) {
    imageFile = e.target.files[0]
    const reader = new FileReader()
    reader.onload = (x) => {
      profileSrc = x.target.result
      profileCible.setAttribute('src', profileSrc)
    }
    reader.readAsDataURL(imageFile)
  } else {
    profileCible.setAttribute('src', profileView)
  }
}
